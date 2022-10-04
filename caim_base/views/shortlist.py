from django.core.exceptions import BadRequest
from django.http import JsonResponse
from ..models import Animal, AnimalShortList
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@login_required()
@require_http_methods(["POST"])
def api(request):
    if not request.POST["animalId"]:
        raise BadRequest("Missing params")
    animal = Animal.objects.filter(id=request.POST["animalId"]).first()
    user = request.user
    if not user or not animal:
        raise BadRequest("Params invalid")
    if request.POST["isSet"] == "true":
        a = AnimalShortList(user=user, animal=animal)
        a.save()
    else:
        a = AnimalShortList.objects.filter(user=user, animal=animal).first()
        if a:
            a.delete()

    return JsonResponse({"ok": True})
