from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from caim_base.views.awg.user_permissions import (
    check_awg_user_permissions_update_context,
)

from ...animal_search import query_animals
from ...models.animals import AnimalShortList
from ...models.awg import Awg


def view(request, awg_id):
    awg = get_object_or_404(Awg, pk=awg_id)

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

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name}",
        "animals": animals,
        "paginator": paginator,
        "shortlistAnimalIds": shortlist_animal_ids,
    }
    context = check_awg_user_permissions_update_context(request, awg, None, context)

    return render(request, "awg/view.html", context)
