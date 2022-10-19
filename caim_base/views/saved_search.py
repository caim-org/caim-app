from django.core.exceptions import BadRequest
from django.http import JsonResponse
from ..models import Animal, AnimalShortList
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@login_required()
@require_http_methods(["POST"])
def add(request):
    return JsonResponse({"ok": True})
