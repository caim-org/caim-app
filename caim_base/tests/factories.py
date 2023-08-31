import random
import factory

from django.contrib.gis.geos import Point

from factory.django import DjangoModelFactory
from factory.fuzzy import BaseFuzzyAttribute

from caim_base.models import (
    FosterApplication,
    Animal,
    Awg,
    Breed,
    User,
    FostererProfile
)


class FactoryGISPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0),
                     random.uniform(-90.0, 90.0))


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User


class FostererProfileFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    email = factory.Faker('email')
    firstname = factory.Faker('first_name')
    lastname = factory.Faker('last_name')
    street_address = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')

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
    is_mixed_breed = factory.Faker('pybool')
    is_unknown_breed = factory.Faker('pybool')
    is_spayed_neutered = factory.Faker('pybool')
    is_vaccinations_current = factory.Faker('pybool')
    is_euth_listed = factory.Faker('pybool')
    awg = factory.SubFactory(AwgFactory)
    primary_breed = factory.SubFactory(BreedFactory)
    is_special_needs = factory.Faker('pybool')

    class Meta:
        model = Animal


class FosterApplicationFactory(DjangoModelFactory):
    animal = factory.SubFactory(AnimalFactory)
    fosterer = factory.SubFactory(FostererProfileFactory)

    class Meta:
        model = FosterApplication
