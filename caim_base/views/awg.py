from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator

from ..models import Awg, Animal


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

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name}",
        "animals": animals,
        "paginator": paginator,
    }
    return render(request, "awg/view.html", context)
