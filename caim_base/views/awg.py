from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator

from ..models import Awg, Animal, AnimalShortList


def view(request, awg_id):
    try:
        awg = Awg.objects.get(id=awg_id)
    except Awg.DoesNotExist:
        raise Http404("Awg not found")

    query = Animal.objects.filter(awg_id=awg_id).prefetch_related(
        "primary_breed", "secondary_breed", "awg"
    )

    current_page = request.GET.get("page", 1)
    npp = 24

    all_animals = query.all()
    paginator = Paginator(all_animals, npp)
    animals = paginator.page(current_page)

    if request.user.is_authenticated:
        shortlists = AnimalShortList.objects.filter(user=request.user.id)
        shortlist_animal_ids = [s.animal_id for s in shortlists]
    else:
        shortlist_animal_ids = []

    current_user_can_edit_awg = awg.can_be_edited_by(request.user)

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name}",
        "animals": animals,
        "paginator": paginator,
        "shortlistAnimalIds": shortlist_animal_ids,
        "currentUserCanEdit": current_user_can_edit_awg,
    }
    return render(request, "awg/view.html", context)


def edit(request, awg_id):
    pass
