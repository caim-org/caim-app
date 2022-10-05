import os
import requests
import json
import urllib.request
from . import models
from django.core.files import File


class ImportAnimalError(Exception):
    pass


def load_html(url):
    headers = {
        "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.content.decode("UTF-8")


def extract_animal_data(html):
    try:
        lines = html.split("\n")
        for line in lines:
            if "global.PF.pageConfig =" in line:
                json_data = (line.partition("=")[2]).rstrip(" ;")
                return json.loads(json_data)["animal"]
    except Exception as e:
        print(e)
        return None


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


def create_animal_from_petfinder_data(awg, data):
    primary_breed = None
    secondary_breed = None
    if "primary_breed" in data and data["primary_breed"]:
        primary_breed = lookup_breed(data["primary_breed"])
    if "secondary_breed" in data and data["secondary_breed"]:
        secondary_breed = lookup_breed(data["primary_breed"])

    animal = models.Animal(
        name=data["name"],
        animal_type=models.AnimalType.DOG,
        primary_breed=primary_breed,
        secondary_breed=secondary_breed,
        petfinder_id=data["id"],
        awg=awg,
        is_mixed_breed=data["is_mixed_breed"],
        is_unknown_breed=data.get("is_unknown_breed", False),
        sex=map_sex(data["sex"]),
        size=map_size(data["size"].lower()),
        age=map_age(data["age"].lower()),
        special_needs=data.get("special_needs_notes", "") or "",
        description=data.get("description", "") or "",
        is_special_needs=False,
        is_euth_listed=False,
        is_spayed_neutered="Spay/Neuter" in data["attributes"],
        is_vaccinations_current="Shots Current" in data["attributes"],
        behaviour_dogs=map_behavour(
            data["home_environment_attributes"].get("good_with_dogs", False)
        ),
        behaviour_kids=map_behavour(
            data["home_environment_attributes"].get("good_with_children", False)
        ),
        behaviour_cats=map_behavour(
            data["home_environment_attributes"].get("good_with_cats", False)
        ),
    )
    image_url = data["primary_photo_url"]
    img_result = urllib.request.urlretrieve(image_url)
    animal.primary_photo.save(
        os.path.basename(image_url), File(open(img_result[0], "rb"))
    )
    animal.save()

    if data["photo_urls"]:
        for image_url in data["photo_urls"]:
            if image_url != data["primary_photo_url"]:
                ai = models.AnimalImage(animal=animal)
                img_result = urllib.request.urlretrieve(image_url)
                ai.photo.save(
                    os.path.basename(image_url), File(open(img_result[0], "rb"))
                )
                ai.save()
    return animal


def import_animal_from_petfinder(awg, url):
    print("Petfinder import")
    print(url)

    if not "www.petfinder.com" in url:
        raise ImportAnimalError(
            "Can only import animals from www.petfinder.com. Please check URL."
        )

    try:
        html = load_html(url)
    except Exception as e:
        print(e)
        raise ImportAnimalError("Could not load webpage. Please check URL.")

    data = extract_animal_data(html)
    if not data:
        raise ImportAnimalError(
            "Could not extract animal data from page. Please check URL."
        )
    print(data)

    try:
        animal = create_animal_from_petfinder_data(awg, data)
    except Exception as e:
        print(e)
        if e.__class__.__name__ == "IntegrityError":
            raise ImportAnimalError("An animal with this petfinder ID already exists.")
        else:
            raise ImportAnimalError("Could not create animal. Please check URL.")

    return animal
