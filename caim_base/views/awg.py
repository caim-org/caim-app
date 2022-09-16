from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator

from ..models import Awg, AnimalShortList
from ..animal_search import query_animals


def view(request, awg_id):
    try:
        awg = Awg.objects.get(id=awg_id)
    except Awg.DoesNotExist:
        raise Http404("Awg not found")

    current_page = request.GET.get("page", 1)
    npp = 21

    query = query_animals(request.user, awg_id=awg.id)

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
