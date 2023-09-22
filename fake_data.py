import csv
import json
import os
import urllib.request
from random import choice, choices, randint
from typing import List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import transaction
from faker import Faker

from caim_base.models.animals import Animal, AnimalImage, AnimalType, Breed, ZipCode
from caim_base.models.awg import Awg, AwgMember
from caim_base.models.fosterer import (
    FosterApplication,
    FosterApplicationAnimalSuggestion,
    FostererProfile,
    TypeOfAnimals,
    YesNo,
)

assert not settings.PRODUCTION, "CANNOT RUN GENERATE FAKE DATA IN PRODUCTION"

fake = Faker()

User = get_user_model()


def load_zips():
    ZipCode.objects.all().delete()
    file_name = "seed_data/zips.txt"
    with open(file_name) as csv_file:
        zips = []
        csv_reader = csv.reader(csv_file, delimiter=",")

        for row in csv_reader:
            p = ZipCode(
                zip_code=row[0],
                geo_location=Point(float(row[2]), float(row[1])),
            )
            zips.append(p)

        ZipCode.objects.bulk_create(zips)


def load_breeds(animal_type, file_name):
    f = open(file_name)
    breeds = json.load(f)

    with transaction.atomic():
        for handle in breeds:
            name = breeds[handle]
            b = Breed(name=name, slug=handle, animal_type=animal_type.upper())
            b.save()

    f.close()


def map_age(str):
    if str == "baby":
        return Animal.AnimalAge.BABY
    if str == "young":
        return Animal.AnimalAge.YOUNG
    if str == "adult":
        return Animal.AnimalAge.ADULT
    if str == "senior":
        return Animal.AnimalAge.SENIOR


def map_size(str):
    if str == "small":
        return Animal.AnimalSize.S
    if str == "medium":
        return Animal.AnimalSize.M
    if str == "large":
        return Animal.AnimalSize.L
    return None


def map_behavour(v):
    if v is True:
        return Animal.AnimalBehaviourGrade.GOOD
    if v is False:
        return Animal.AnimalBehaviourGrade.POOR
    return Animal.AnimalBehaviourGrade.NOT_TESTED


def map_sex(v):
    v = v.lower()
    if v == "female":
        return Animal.AnimalSex.F
    if v == "male":
        return Animal.AnimalSex.M
    return None


def lookup_breed(pfbreed):
    return Breed.objects.filter(slug=pfbreed["slug"]).first()


def upsert_awg(name, pf_id, city, state, zip, lat, lng):
    awg = Awg.objects.filter(petfinder_id=pf_id).first()
    if not awg:
        awg = Awg(
            name=name,
            petfinder_id=pf_id,
            city=city,
            state=state,
            zip_code=zip,
            geo_location=Point(lng, lat),
            status=Awg.AwgStatus.PUBLISHED,
        )
        awg.save()

    return awg


def load_animals(animal_type, file_name):
    f = open(file_name)
    animals = json.load(f)

    for hash_id in animals:
        try:
            a = animals[hash_id]
            aa = a["animal"]
            pf_id = aa["id"]
            print(a)
            print(aa)

            primary_breed = None
            secondary_breed = None
            if "primary_breed" in aa and aa["primary_breed"]:
                primary_breed = lookup_breed(aa["primary_breed"])
            if "secondary_breed" in aa and aa["secondary_breed"]:
                secondary_breed = lookup_breed(aa["primary_breed"])

            aorg = a["organization"]
            awg_pf_id = aorg["display_id"]

            awg = upsert_awg(
                aorg["name"],
                awg_pf_id,
                a["location"]["address"]["city"],
                a["location"]["address"]["state"],
                a["location"]["address"]["postal_code"],
                float(a["location"]["geo"]["latitude"]),
                float(a["location"]["geo"]["longitude"]),
            )

            print(aa)
            a = Animal(
                name=aa["name"],
                animal_type=AnimalType.DOG,
                primary_breed=primary_breed,
                secondary_breed=secondary_breed,
                petfinder_id=pf_id,
                is_published=True,
                awg_id=awg.id,
                is_mixed_breed=aa["is_mixed_breed"],
                is_unknown_breed=aa.get("is_unknown_breed", False),
                sex=map_sex(aa["sex"]),
                size=map_size(aa["size"].lower()),
                age=map_age(aa["age"].lower()),
                special_needs=aa.get("special_needs_notes", "") or "",
                description=aa.get("description", "") or "",
                is_special_needs=False,
                is_euth_listed=False,
                euth_date=fake.date_between(start_date="today", end_date="+30d"),
                is_spayed_neutered="Spay/Neuter" in aa["attributes"],
                is_vaccinations_current="Shots Current" in aa["attributes"],
                behaviour_dogs=map_behavour(
                    aa["home_environment_attributes"].get("good_with_dogs", False)
                ),
                behaviour_kids=map_behavour(
                    aa["home_environment_attributes"].get("good_with_children", False)
                ),
                behaviour_cats=map_behavour(
                    aa["home_environment_attributes"].get("good_with_cats", False)
                ),
            )
            image_url = aa["primary_photo_url"]
            img_result = urllib.request.urlretrieve(image_url)
            a.primary_photo.save(
                os.path.basename(image_url), File(open(img_result[0], "rb"))
            )
            a.save()

            if aa["photo_urls"]:
                for image_url in aa["photo_urls"]:
                    print(image_url)
                    if image_url != aa["primary_photo_url"]:
                        ai = AnimalImage(animal=a)
                        img_result = urllib.request.urlretrieve(image_url)
                        ai.photo.save(
                            os.path.basename(image_url), File(open(img_result[0], "rb"))
                        )
                        ai.save()
        except Exception as er:
            print(er)
            print("SKIPPEd")


def fake_foster_profile(user: User) -> FostererProfile:
    fosterer = FostererProfile()
    fosterer.user = user
    fosterer.firstname = fake.first_name()
    fosterer.lastname = fake.last_name()
    fosterer.email = user.email
    fosterer.phone = fake.phone_number()
    try:
        fosterer.full_clean()
    except ValidationError as exc:
        phone_broke = exc.error_dict.get("phone", None)
        if phone_broke:
            fosterer.phone = None
        # lots of other fields are likely invalid here, don't raise
    fosterer.street_address = fake.address()
    fosterer.city = fake.city()[: FostererProfile.city.field.max_length - 1]
    fosterer.state = fake.state_abbr()
    fosterer.zip_code = fake.zipcode()
    # pick a random selections from these ChoiceArrayFields
    # from 1-max number of selections
    k = randint(1, len(TypeOfAnimals.choices))
    fosterer.type_of_animals = list(
        set(choices([choice[0] for choice in TypeOfAnimals.choices], k=k))
    )
    k = randint(1, len(fosterer.CategoryOfAnimals.choices))
    fosterer.category_of_animals = list(
        set(choices([choice[0] for choice in fosterer.CategoryOfAnimals.choices], k=k))
    )
    k = randint(1, len(fosterer.BehaviouralAttributes.choices))
    fosterer.behavioural_attributes = list(
        set(
            choices(
                [choice[0] for choice in fosterer.BehaviouralAttributes.choices], k=k
            )
        )
    )
    fosterer.timeframe = choice([choice[0] for choice in fosterer.Timeframe.choices])
    # if fosterer.Timeframe.ANY_DURATION in fosterer.timeframe:
    #     fosterer.timeframe_other = fake.text(randint(5, 500))
    fosterer.num_existing_pets = randint(0, 10)
    # fosterer.existing_pets_details = fake.text(randint(5, 500))
    fosterer.experience_description = fake.text(randint(5, 500))
    # pick a random selections from these choice fields, from 1-max number of selections
    k = randint(1, len(fosterer.ExperienceCategories.choices))
    fosterer.experience_categories = list(
        set(
            choices(
                [choice[0] for choice in fosterer.ExperienceCategories.choices], k=k
            )
        )
    )
    fosterer.experience_given_up_pet = fake.text(randint(5, 500))
    fosterer.reference_1 = fake.name()
    fosterer.reference_2 = fake.name()
    fosterer.reference_3 = fake.name()
    fosterer.people_at_home = fake.text(randint(5, 50))
    # from just normal choice fields, pick 1 choice
    fosterer.yard_type = choice([choice[0] for choice in fosterer.YardTypes.choices])
    fosterer.yard_fence_over_5ft = choice([choice[0] for choice in YesNo.choices])
    fosterer.rent_own = choice([choice[0] for choice in fosterer.RentOwn.choices])
    if fosterer.rent_own == fosterer.RentOwn.RENT:
        fosterer.rent_restrictions = fake.text(randint(5, 50))
        # fosterer.rent_ok_foster_pets = choice([choice[0] for choice in YesNo.choices])
    else:
        fosterer.rent_restrictions = None
        # fosterer.rent_ok_foster_pets = YesNo.YES  # field not allowing null???
    fosterer.hours_alone_description = fake.text(10)
    fosterer.hours_alone_location = fake.text(10)
    fosterer.sleep_location = fake.text(10)
    fosterer.other_info = fake.text(50)
    fosterer.ever_been_convicted_abuse = choice([choice[0] for choice in YesNo.choices])
    fosterer.agree_share_details = choice([choice[0] for choice in YesNo.choices])
    fosterer.is_complete = choice([True, False])
    fosterer.medical_issues = choice([choice[0] for choice in YesNo.choices])
    fosterer.special_needs = choice([choice[0] for choice in YesNo.choices])
    fosterer.behavioral_issues = choice([choice[0] for choice in YesNo.choices])
    fosterer.all_in_agreement = choice([choice[0] for choice in YesNo.choices])
    fosterer.stairs = choice([choice[0] for choice in YesNo.choices])
    fosterer.agree_social_media = choice([choice[0] for choice in YesNo.choices])
    fosterer.pet_allergies = choice([choice[0] for choice in YesNo.choices])
    fosterer.full_clean()
    return fosterer


def fake_fosterers(num_desired_fosterers: int):
    print("generating fake fosterers...")
    for _ in range(num_desired_fosterers):
        # going through the fields in the same order they appear in the model
        try:
            user = User.objects.create_user(fake.user_name(), email=fake.email())
        except django.db.IntegrityError:
            # Random name collision gives an IntegrityError, but odds getting two IntegrityError in a row here has got
            # to be very, very low.
            user = User.objects.create_user(fake.user_name(), email=fake.email())

        user.save()
        fosterer = fake_foster_profile(user)
        fosterer.save()


def fake_foster_application(
    animal: Animal, foster_profile: FostererProfile
) -> FosterApplication:
    application = FosterApplication()
    application.animal = animal
    application.fosterer = foster_profile.copy_to_static()
    application.status = choice([choice[0] for choice in application.Statuses.choices])
    if application.status == application.Statuses.REJECTED:
        application.reject_reason = choice(
            [choice[0] for choice in application.RejectionReasons.choices]
        )
        application.reject_reason_detail = fake.text(1000)
    else:
        application.reject_reason = choice(
            [choice[0] for choice in application.RejectionReasons.choices]
        )
    application.full_clean()
    return application


def fake_foster_applications():
    print("generating a bunch of fake foster applications for each animal...")
    animals = Animal.objects.all()
    fosterers = FostererProfile.objects.all()
    applications = []
    for animal in animals:
        for _ in range(5):
            fosterer = choice(fosterers)
            application = fake_foster_application(animal, fosterer)
            applications.append(application)
    FosterApplication.objects.bulk_create(applications)


def fake_foster_application_suggestion(suggestions_per_awg: int = 2):
    print(
        "generating some alernative suggested animals"
        "for a few of the rejected applications in each awg"
    )
    awgs = Awg.objects.all()
    for awg in awgs:
        applications = FosterApplication.objects.select_related("animal").filter(
            animal__awg=awg,
            status__in=[
                FosterApplication.Statuses.ACCEPTED,
                FosterApplication.Statuses.REJECTED,
            ],
        )
        suggestions_per_awg = min(suggestions_per_awg, applications.count())
        if suggestions_per_awg:
            continue
            # next awg, there wasn't any accepted or rejected applications here
        get_suggest: List[FosterApplication] = choices(
            list(applications), k=suggestions_per_awg
        )
        for application_gets_suggest in get_suggest:
            animals_could_suggest = Animal.objects.filter(awg=awg).exclude(
                pk=application_gets_suggest.animal.id
            )
            # some awgs only have one animal
            if animals_could_suggest.count() > 0:
                animal = choice(animals_could_suggest)
                suggestion = FosterApplicationAnimalSuggestion(
                    application=application_gets_suggest, animal=animal
                )
                suggestion.save()


def fake_user_didnothing():
    print(
        "registering a fake user to use for testing a user w/ no applications"
        " and not in an AWG:"
    )
    print("username&pass: testuser")
    user = User.objects.create_user(
        "testuser", password="testuser", email="testuser@caim.org"
    )
    user.save()


def fake_staff_user():
    print("registering a fake caim staff user")
    print("username&pass: teststaff")
    user = User.objects.create_user(
        "teststaff", password="teststaff", email="teststaff@caim.org"
    )
    user.is_staff = True
    user.save()


def fake_user_with_foster_profile_and_applications():
    print(
        "registering a fake user to use for testing a user w/ an application,"
        " and not in an AWG"
    )
    print("username&pass: testfosterer")
    user = User.objects.create_user(
        "testfosterer", password="testfosterer", email="testfosterer@caim.org"
    )
    user.save()
    profile = fake_foster_profile(user)
    profile.save()
    # make a few applications
    fake_foster_application(choice(Animal.objects.all()), profile)
    fake_foster_application(choice(Animal.objects.all()), profile)
    fake_foster_application(choice(Animal.objects.all()), profile)
    fake_foster_application(choice(Animal.objects.all()), profile)
    fake_foster_application(choice(Animal.objects.all()), profile)
    fake_foster_application(choice(Animal.objects.all()), profile)


def fake_user_in_awg():
    print("registering a fake user in an AWG with full permissions")
    print("username&pass: testawg")
    user = User.objects.create_user(
        "testawg", password="testawg", email="testawg@caim.org"
    )
    user.save()
    awgmembership = AwgMember()
    awgmembership.user = user
    awgmembership.awg = choice(Awg.objects.all())
    awgmembership.canEditProfile = True
    awgmembership.canManageAnimals = True
    awgmembership.canManageMembers = True
    awgmembership.canManageApplications = True
    awgmembership.save()


def fake_user_in_awg_appviewonly():
    print(
        "registering a fake user in an AWG that cannot manage applications,"
        " only view them"
    )
    print("username&pass: testawg_viewapps")
    user = User.objects.create_user(
        "testawg_viewapps",
        password="testawg_viewapps",
        email="testawg_viewapps@caim.org",
    )
    user.save()
    awgmembership = AwgMember()
    awgmembership.user = user
    awgmembership.awg = choice(Awg.objects.all())
    awgmembership.canEditProfile = True
    awgmembership.canManageAnimals = True
    awgmembership.canManageMembers = True
    awgmembership.canManageApplications = False
    awgmembership.canViewApplications = True
    awgmembership.save()
