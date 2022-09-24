from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import Http404

from ...models import Awg, Animal


def list_animals(request, awg_id):
    try:
        awg = Awg.objects.get(id=awg_id)
    except Awg.DoesNotExist:
        raise Http404("Awg not found")

    current_user_permissions = awg.get_permissions_for_user(request.user)
    if not "MANAGE_MEMBERS" in current_user_permissions:
        raise PermissionDenied(
            "User does not have permission to manage members for this AWG"
        )

    animals = []

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name} | Animals",
        "currentUserPermissions": current_user_permissions,
        "animals": animals,
    }
    return render(request, "awg/manage/list-animals.html", context)
