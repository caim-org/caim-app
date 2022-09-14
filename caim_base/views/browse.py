from datetime import timedelta, datetime
from django.shortcuts import render
from django.db.models import Q
from django.core.exceptions import BadRequest
from django.core.paginator import Paginator
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

from ..models import Animal, Breed, ZipCode, AnimalType, AnimalShortList


def parse_radius(args):
    if not args.get("zip"):
        return "any"
    if "radius" not in args:
        return 50
    if args["radius"] == "any":
        return None
    return int(args["radius"])


def parse_euth_date(args):
    if "euth_date" not in args:
        return None
    if args["euth_date"].isnumeric():
        return int(args["euth_date"])
    return None


def view(request):
    animal_type = AnimalType.DOG

    breeds = Breed.objects.filter(animal_type=animal_type).all()

    search = {
        "zip": request.GET.get("zip"),
        "radius": parse_radius(request.GET),
        "breed": request.GET.get("breed", "").lower(),
        "age": request.GET.get("age", "").lower(),
        "sex": request.GET.get("sex", "").lower(),
        "euth_date": parse_euth_date(request.GET),
        "sort": request.GET.get("sort", "distance").lower(),
        "page": int(request.GET.get("page", 1)),
        "npp": int(request.GET.get("limit", 21)),
        "purebreed": request.GET.get("purebreed", "") == "on",
        "goodwith_cats": request.GET.get("goodwith_cats", "") == "on",
        "goodwith_dogs": request.GET.get("goodwith_dogs", "") == "on",
        "goodwith_kids": request.GET.get("goodwith_kids", "") == "on",
        "shortlist": request.GET.get("shortlist", "") == "on",
    }

    zip = None
    if search["zip"]:
        zip = ZipCode.objects.filter(zip_code=search["zip"]).first()
        if not zip:
            raise BadRequest("Invalid ZIP parameter")

    query = Animal.objects.filter(animal_type=animal_type).prefetch_related(
        "primary_breed", "secondary_breed", "awg"
    )

    if zip:
        query = query.annotate(distance=Distance("awg__geo_location", zip.geo_location))

    if search["age"]:
        query = query.filter(age=search["age"].upper())

    if search["euth_date"]:
        td = timedelta(days=search["euth_date"])
        # @todo timezone (UTC by default)
        future_date = (datetime.now() + td).replace(hour=23, minute=59, second=59)
        query = query.filter(euth_date__lte=future_date)

    if search["sex"]:
        query = query.filter(sex=search["sex"].upper())

    if search["breed"]:
        query = query.filter(
            Q(primary_breed__slug=search["breed"])
            | Q(secondary_breed__slug=search["breed"])
        )

    if search["purebreed"]:
        query = query.filter(is_mixed_breed=False)

    if search["goodwith_cats"]:
        query = query.filter(behaviour_cats=Animal.AnimalBehaviourGrade.GOOD)

    if search["goodwith_dogs"]:
        query = query.filter(behaviour_dogs=Animal.AnimalBehaviourGrade.GOOD)

    if search["goodwith_kids"]:
        query = query.filter(behaviour_kids=Animal.AnimalBehaviourGrade.GOOD)

    if search["radius"] and zip:
        radius_meters = search["radius"] * 1609.34
        query = query.filter(distance__lte=radius_meters)

    if search["sort"]:
        sortby = search["sort"]
        if sortby == "distance" and not zip:
            sortby = "-created_at"
            search["sort"] = sortby
        query = query.order_by(sortby, "id")

    if request.user.is_authenticated:
        shortlists = AnimalShortList.objects.filter(user=request.user.id)
        shortlist_animal_ids = [s.animal_id for s in shortlists]
    else:
        shortlist_animal_ids = []
    if search["shortlist"] and request.user.id:
        query = query.filter(id__in=shortlist_animal_ids)

    all_animals = query.all()
    paginator = Paginator(all_animals, search["npp"])
    animals = paginator.page(search["page"])

    context = {
        "animals": animals,
        "search": search,
        "breeds": breeds,
        "pageTitle": "Browse animals",
        "shortlistAnimalIds": shortlist_animal_ids,
        "paginator": paginator,
    }
    return render(request, "browse.html", context)
