from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ..models.animals import AnimalType, Breed, SavedSearch


# Calculate the default name label for a given saved search config
# This is just to give an initial sensible name for the search, but the user
# can change it later
def calculate_saved_search_name(search):
    parts = []

    if search["breed"]:
        parts.append(search["breed"].capitalize())

    if search["animal_type"]:
        parts.append(AnimalType.pluralize(search["animal_type"]).lower())

    if search["zip_code"]:
        if search["radius"] == "any":
            parts.append("anywhere")
        elif search["radius"]:
            miles = search["radius"]
            zip = search["zip_code"]
            parts.append(f"within {miles} miles of {zip}")

    return " ".join(parts)


@login_required()
@require_http_methods(["POST"])
def add(request):
    params = {
        "animal_type": request.POST.get("animal_type") or None,
        "zip_code": request.POST.get("zip") or None,
        "radius": request.POST.get("radius") or None,
        "age": request.POST.get("age") or None,
        "size": request.POST.get("size") or None,
        "sex": request.POST.get("sex") or None,
        "breed": request.POST.get("breed") or None,
        "euth_date_within_days": request.POST.get("euth_date_within_days") or None,
        "goodwith_cats": request.POST.get("goodwith_cats") == "true",
        "goodwith_dogs": request.POST.get("goodwith_dogs") == "true",
        "goodwith_kids": request.POST.get("goodwith_kids") == "true",
    }

    # Need to lookup Breed model if selected
    breed = None
    if params["breed"]:
        breed = Breed.objects.get(slug=params["breed"])

    # Radius can be "any" but its stored in db as None
    radius = None if params["radius"] == "any" else params["radius"]

    # Check for existing saved search for this user with same params
    # If one exists, we dont add a new one and return a payload with existing=True
    existing_row = SavedSearch.objects.filter(
        user=request.user,
        animal_type=params["animal_type"],
        breed=breed,
        zip_code=params["zip_code"],
        radius=radius,
        age=params["age"],
        size=params["size"],
        sex=params["sex"],
        euth_date_within_days=params["euth_date_within_days"],
        goodwith_cats=params["goodwith_cats"],
        goodwith_dogs=params["goodwith_dogs"],
        goodwith_kids=params["goodwith_kids"],
    ).first()

    if existing_row:
        return JsonResponse(
            {
                "ok": True,
                "name": existing_row.name,
                "id": existing_row.id,
                "existing": True,
            }
        )

    saved_search = SavedSearch(
        user=request.user,
        name=calculate_saved_search_name(params),
        animal_type=params["animal_type"],
        breed=breed,
        zip_code=params["zip_code"],
        radius=radius,
        age=params["age"],
        size=params["size"],
        sex=params["sex"],
        euth_date_within_days=params["euth_date_within_days"],
        goodwith_cats=params["goodwith_cats"],
        goodwith_dogs=params["goodwith_dogs"],
        goodwith_kids=params["goodwith_kids"],
    )
    saved_search.save()

    return JsonResponse(
        {
            "ok": True,
            "name": saved_search.name,
            "id": saved_search.id,
            "existing": False,
        }
    )
