from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.gis.db.models.functions import Distance

from ..animal_search import query_animals

from ..models.animals import Breed, AnimalType, AnimalShortList, SavedSearch
from ..models.geo import ZipCode


def parse_radius(args):
    if not args.get("zip"):
        return None
    if "radius" not in args:
        return None  # Temp change to default to any not 50
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
    if request.GET.get("animal_type") == "CAT":
        animal_type = AnimalType.CAT
    elif request.GET.get("animal_type") == "DOG":
        animal_type = AnimalType.DOG
    else:
        animal_type = None

    breeds = Breed.objects.all()
    if animal_type:
        breeds = breeds.filter(animal_type=animal_type)

    search = {
        "animal_type": animal_type,
        "zip": request.GET.get("zip"),
        "radius": parse_radius(request.GET),
        "breed": request.GET.get("breed", "").lower(),
        "age": request.GET.get("age", "").lower(),
        "size": request.GET.get("size", "").lower(),
        "sex": request.GET.get("sex", "").lower(),
        "euth_date_within_days": parse_euth_date(request.GET),
        "sort": request.GET.get("sort", "distance").lower(),
        "goodwith_cats": request.GET.get("goodwith_cats", "") == "on",
        "goodwith_dogs": request.GET.get("goodwith_dogs", "") == "on",
        "goodwith_kids": request.GET.get("goodwith_kids", "") == "on",
        "shortlist": request.GET.get("shortlist", "") == "on",
    }
    if not search["zip"] and search["sort"] == "distance":
        search["sort"] = "-created_at"

    current_page = int(request.GET.get("page", 1))
    npp = int(request.GET.get("limit", 21))

    query = query_animals(request.user, **search)

    if request.user.is_authenticated:
        shortlists = AnimalShortList.objects.filter(user=request.user.id)
        shortlist_animal_ids = [s.animal_id for s in shortlists]
        saved_searches = SavedSearch.objects.filter(user=request.user.id)
    else:
        shortlist_animal_ids = []
        saved_searches = []

    all_animals = query.all()
    paginator = Paginator(all_animals, npp)
    animals = paginator.page(current_page)

    context = {
        "animals": animals,
        "search": search,
        "breeds": breeds,
        "pageTitle": "Browse animals",
        "shortlistAnimalIds": shortlist_animal_ids,
        "paginator": paginator,
        "savedSearches": saved_searches,
        "animal_type": animal_type,
        "animal_types": dict(AnimalType.choices),
    }
    return render(request, "browse.html", context)
