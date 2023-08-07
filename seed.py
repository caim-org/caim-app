from django.conf import settings
from django.contrib.auth import get_user_model
from caim_base.models.animals import (Animal, AnimalImage, AnimalType, Breed,
                                      ZipCode)
from caim_base.models.awg import Awg, AwgMember
from caim_base.models.fosterer import FosterApplication, FostererProfile

from fake_data import (      
    load_zips,
    load_breeds,
    load_breeds,
    load_animals,
    load_animals,
    load_animals,
    fake_fosterers,
    fake_foster_applications,
    fake_user_didnothing,
    fake_staff_user,
    fake_user_in_awg,
    fake_user_in_awg_appviewonly,
    fake_user_with_foster_profile_and_applications,
)

User = get_user_model()
assert not settings.PRODUCTION, "CANNOT RUN SEED.PY IN PRODUCTION"

Animal.objects.all().delete()
Awg.objects.all().delete()
Breed.objects.all().delete()
User.objects.all().delete()
FostererProfile.objects.all().delete()
FosterApplication.objects.all().delete()

load_zips()
load_breeds("dog", "seed_data/dog-breeds.json")
load_breeds("cat", "seed_data/cat-breeds.json")

load_animals("dog", "seed_data/dogs.json")
load_animals("dog", "seed_data/dogs2.json")
load_animals("dog", "seed_data/dogs3.json")

fake_fosterers(100)
fake_foster_applications()

fake_user_didnothing()
fake_staff_user()
fake_user_in_awg()
fake_user_in_awg_appviewonly()
fake_user_with_foster_profile_and_applications()
