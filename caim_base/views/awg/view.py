from django.shortcuts import render, redirect
from django.http import Http404
from django.core.paginator import Paginator

from ...models.animals import AnimalShortList
from ...models.awg import Awg
from ...animal_search import query_animals


def view(request, awg_id):
    try:
        awg = Awg.objects.get(id=awg_id)
    except Awg.DoesNotExist:
        raise Http404("Awg not found")

    # If not published AND current user is not a staff member, redirect
    if (
        not awg.status == "PUBLISHED"
        and not awg.user_is_member_of_awg(request.user)
        and not request.user.is_staff
    ):
        return redirect("/")

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

    current_user_permissions = awg.get_permissions_for_user(request.user)

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name}",
        "animals": animals,
        "paginator": paginator,
        "shortlistAnimalIds": shortlist_animal_ids,
        "currentUserPermissions": current_user_permissions,
    }
    return render(request, "awg/view.html", context)
