import random
import factory

from django.contrib.gis.geos import Point

from factory.django import DjangoModelFactory
from factory import fuzzy
from caim_base.models import (
    FosterApplication,
    Animal,
    Awg,
    Breed,
    User,
    FostererProfile,
    YesNo,
    TypeOfAnimals,
)


class FactoryGISPoint(fuzzy.BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0), random.uniform(-90.0, 90.0))


class UserFactory(DjangoModelFactory):
    username = factory.Faker("email")
    email = factory.Faker("email")

    class Meta:
        model = User


def get_type_of_animals():
    return [random.choice([value for value in TypeOfAnimals.values])]


def get_category_of_animals():
    return [random.choice([value for value in FostererProfile.CategoryOfAnimals.values])]


def get_agree_share_details():
    return [random.choice([value for value in YesNo.values])]

def get_behavioural_attributes():
    return [random.choice([value for value in FostererProfile.BehaviouralAttributes.values])]

def get_ever_been_convicted_abuse():
    return [random.choice([value for value in YesNo.values])]

def get_rent_own():
    return [random.choice([value for value in FostererProfile.RentOwn.values])]

def get_age():
    return random.randint(1, 100)

def get_num_people_in_home():
    return random.randint(1, 6)

def get_agree_social_media():
    return [random.choice([value for value in YesNo.values])]

def get_all_in_agreement():
    return [random.choice([value for value in YesNo.values])]


class FostererProfileFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    email = factory.Faker("email")
    firstname = factory.Faker("first_name")
    lastname = factory.Faker("last_name")
    street_address = factory.Faker("street_address")
    zip_code = factory.Faker("zipcode")
    phone = factory.Faker("phone_number")
    city = factory.Faker("city")
    state = factory.Faker("state_abbr")
    hours_alone_description = factory.Faker("text")
    hours_alone_location = factory.Faker("text")

    type_of_animals = factory.LazyFunction(get_type_of_animals)
    category_of_animals = factory.LazyFunction(get_category_of_animals)
    agree_share_details = factory.LazyFunction(get_agree_share_details)
    behavioural_attributes = factory.LazyFunction(get_behavioural_attributes)
    ever_been_convicted_abuse = factory.LazyFunction(get_ever_been_convicted_abuse)
    age = factory.LazyFunction(get_age)
    rent_own = factory.LazyFunction(get_rent_own)
    sleep_location = factory.Faker("text")
    agree_social_media = factory.LazyFunction(get_agree_social_media)
    all_in_agreement = factory.LazyFunction(get_all_in_agreement)
    num_people_in_home = factory.LazyFunction(get_num_people_in_home)

    class Meta:
        model = FostererProfile


class BreedFactory(DjangoModelFactory):
    class Meta:
        model = Breed


class AwgFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Awg #{n}")
    geo_location = FactoryGISPoint()

    class Meta:
        model = Awg


class AnimalFactory(DjangoModelFactory):
    is_mixed_breed = factory.Faker("pybool")
    is_unknown_breed = factory.Faker("pybool")
    is_spayed_neutered = factory.Faker("pybool")
    is_vaccinations_current = factory.Faker("pybool")
    is_euth_listed = factory.Faker("pybool")
    awg = factory.SubFactory(AwgFactory)
    primary_breed = factory.SubFactory(BreedFactory)
    is_special_needs = factory.Faker("pybool")

    class Meta:
        model = Animal


class FosterApplicationFactory(DjangoModelFactory):
    animal = factory.SubFactory(AnimalFactory)
    fosterer = factory.SubFactory(FostererProfileFactory)

    class Meta:
        model = FosterApplication
