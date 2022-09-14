from django.core.exceptions import BadRequest
from django.http import JsonResponse
from ..models import Animal, AnimalShortList


def api(request):
    if not request.user.is_authenticated:
        raise BadRequest("Must be logged in")
    if request.method == "POST":
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
