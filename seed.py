import csv
import json
from caim_base import models
from django.contrib.gis.geos import Point
from django.db import transaction
from django.core.files import File
import urllib.request
from faker import Faker

fake = Faker()


def load_zips():
    models.ZipCode.objects.all().delete()
    file_name = "seed_data/zips.txt"
    with open(file_name) as csv_file:
        zips = []
        csv_reader = csv.reader(csv_file, delimiter=",")

        for row in csv_reader:
            p = models.ZipCode(
                zip_code=row[0],
                geo_location=Point(float(row[2]), float(row[1])),
            )
            zips.append(p)

        models.ZipCode.objects.bulk_create(zips)


def load_breeds(animal_type, file_name):
    f = open(file_name)
    breeds = json.load(f)

    with transaction.atomic():
        for handle in breeds:
            name = breeds[handle]
            b = models.Breed(name=name, slug=handle, animal_type=animal_type.upper())
            b.save()

    f.close()


def map_age(str):
    if str == "baby":
        return models.Animal.AnimalAge.BABY
    if str == "young":
        return models.Animal.AnimalAge.YOUNG
    if str == "adult":
        return models.Animal.AnimalAge.ADULT
    if str == "senior":
        return models.Animal.AnimalAge.SENIOR


def map_size(str):
    if str == "small":
        return models.Animal.AnimalSize.S
    if str == "medium":
        return models.Animal.AnimalSize.M
    if str == "large":
        return models.Animal.AnimalSize.L
    return None


def map_behavour(v):
    if v == True:
        return models.Animal.AnimalBehaviourGrade.GOOD
    if v == False:
        return models.Animal.AnimalBehaviourGrade.POOR
    return models.Animal.AnimalBehaviourGrade.NOT_TESTED


def map_sex(v):
    v = v.lower()
    if v == "female":
        return models.Animal.AnimalSex.F
    if v == "male":
        return models.Animal.AnimalSex.M
    return None


def lookup_breed(pfbreed):
    return models.Breed.objects.filter(slug=pfbreed["slug"]).first()


def upsert_awg(name, pf_id, city, state, zip, lat, lng):
    awg = models.Awg.objects.filter(petfinder_id=pf_id).first()
    if not awg:
        awg = models.Awg(
            name=name,
            petfinder_id=pf_id,
            city=city,
            state=state,
            zip_code=zip,
            geo_location=Point(lng, lat),
            is_published=True,
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
            a = models.Animal(
                name=aa["name"],
                animal_type=models.AnimalType.DOG,
                primary_breed=primary_breed,
                secondary_breed=secondary_breed,
                petfinder_id=pf_id,
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
                        ai = models.AnimalImage(animal=a)
                        img_result = urllib.request.urlretrieve(image_url)
                        ai.photo.save(
                            os.path.basename(image_url), File(open(img_result[0], "rb"))
                        )
                        ai.save()
        except Exception as er:
            print(er)
            print("SKIPPEd")


models.Animal.objects.all().delete()
models.Awg.objects.all().delete()
models.Breed.objects.all().delete()

load_zips()
load_breeds("dog", "seed_data/dog-breeds.json")
load_breeds("cat", "seed_data/cat-breeds.json")

load_animals("dog", "seed_data/dogs.json")
load_animals("dog", "seed_data/dogs2.json")
load_animals("dog", "seed_data/dogs3.json")
