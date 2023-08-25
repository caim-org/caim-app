from django.shortcuts import render, redirect
from django.http import Http404
from ..models.animals import Animal, AnimalShortList, AnimalComment


def view(request, animal_id):
    try:
        animal = Animal.objects.get(id=animal_id)
    except Animal.DoesNotExist as e:
        raise Http404("Animal not found") from e

    awg = animal.awg
    # If the animal listing is not published
    # OR if the aws is not published
    # AND the user is not staff
    # we redirect
    if (
        (not animal.is_currently_published())
        and not awg.user_is_member_of_awg(request.user)
        and not request.user.is_staff
    ):
        return redirect("/")

    is_shortlisted = False
    if request.user.id:
        is_shortlisted = AnimalShortList.objects.filter(
            user=request.user, animal=animal
        ).exists()

    comments = (
        AnimalComment.objects.filter(animal=animal)
        .prefetch_related("user")
        .order_by("created_at")
        .all()
    )

    context = {
        "animal": animal,
        "isShortlisted": is_shortlisted,
        "pageTitle": f"{animal.name} | {animal.animal_type.title()}",
        "comments": comments,
        "commentCount": len(comments),
        "images": animal.animalimage_set.all(),
        "himHer": "her" if animal.sex == Animal.AnimalSex.F else "him",
    }
    return render(request, "animal/view.html", context)
