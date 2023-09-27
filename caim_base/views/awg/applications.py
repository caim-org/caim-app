from textwrap import dedent
from typing import Optional, Tuple

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from caim_base.models.animals import Animal
from caim_base.models.awg import Awg
from caim_base.models.fosterer import (
    FosterApplication,
    FosterApplicationAnimalSuggestion,
)
from caim_base.notifications import (
    notify_caim_of_animal_suggestion,
    notify_caim_foster_application_accepted,
    notify_caim_foster_application_rejected,
)
from caim_base.views.awg.user_permissions import (
    check_awg_user_permissions_update_context,
)


def query_applications_for_awg(
    awg: Awg, order_by: Optional[Tuple[str]] = None, status: Optional[str] = None
) -> QuerySet:
    applications = FosterApplication.objects.select_related("animal").filter(
        animal__awg=awg
    )
    if status:
        applications = applications.filter(status=status)
    if order_by is None:
        order_by = ("-submitted_on", "fosterer__lastname", "fosterer__firstname")
    applications = applications.order_by(*order_by)
    return applications


@login_required()
@require_http_methods(["GET"])
def list_applications(request, awg_id):
    awg = get_object_or_404(Awg, pk=awg_id)
    filters = {"status": request.GET.get("status", None)}
    applications = query_applications_for_awg(awg, **filters)
    context = {
        "filters": filters,
        "awg": awg,
        "applications": applications,
        "application_status_options": [
            c[0] for c in FosterApplication.Statuses.choices
        ],
    }
    try:
        context = check_awg_user_permissions_update_context(
            request, awg, ["MANAGE_APPLICATIONS"], context
        )
    except PermissionDenied:
        try:
            context = check_awg_user_permissions_update_context(
                request, awg, ["VIEW_APPLICATIONS"], context
            )
        except PermissionDenied as e:
            raise PermissionDenied(
                "User does not have permissions to view or manage applications"
            ) from e

    return render(request, "awg/manage/applications/list.html", context)


@login_required()
@require_http_methods(["POST"])
def update_application_status_submit_modal(request, awg_id, application_id):
    awg = get_object_or_404(Awg, pk=awg_id)

    context = check_awg_user_permissions_update_context(
        request, awg, ["MANAGE_APPLICATIONS"]
    )
    application: FosterApplication = get_object_or_404(
        FosterApplication, id=application_id, animal__awg=awg
    )
    new_status = request.POST.get("status")
    if new_status is not None:
        # this is lame is there any better way to do this
        if new_status.upper() not in [t[0] for t in FosterApplication.Statuses.choices]:
            return HttpResponse(
                dedent(
                    f"""
                    <h1>400 Invalid</h1>
                    <div>Invalid POST parameter "status": {new_status}</div>
                    <div>Valid Options:{FosterApplication.Statuses.choices}</div>
                """
                ),
                status=400,
            )
        application.status = new_status.upper()
    application.reject_reason = request.POST.get("reject_reason")
    application.reject_reason_detail = request.POST.get("reject_reason_detail")
    application.save()

    notify = {
        FosterApplication.Statuses.ACCEPTED: notify_caim_foster_application_accepted,
        FosterApplication.Statuses.REJECTED: notify_caim_foster_application_rejected,
    }
    notify[application.status](application)

    templates = {
        FosterApplication.Statuses.ACCEPTED: (
            "awg/manage/applications/accept_confirmed_modal.html"
        ),
        FosterApplication.Statuses.REJECTED: (
            "awg/manage/applications/reject_confirmed_modal.html",
        ),
    }
    template = templates[application.status]

    context = {
        **context,
        "awg": awg,
        "app": application,
    }
    return render(request, template, context)


@login_required()
@require_http_methods(["GET"])
def update_application_status_modal(request, awg_id, application_id, status):
    awg: Awg = get_object_or_404(Awg, pk=awg_id)
    context = check_awg_user_permissions_update_context(
        request, awg, ["MANAGE_APPLICATIONS"]
    )
    application: FosterApplication = get_object_or_404(
        FosterApplication, id=application_id, animal__awg=awg
    )

    templates = {
        FosterApplication.Statuses.ACCEPTED: (
            "awg/manage/applications/accept_modal.html"
        ),
        FosterApplication.Statuses.REJECTED: (
            "awg/manage/applications/reject_modal.html"
        ),
    }
    template = templates[status]

    context = {
        **context,
        "awg": awg,
        "app": application,
        "reject_reasons": FosterApplication.RejectionReasons.choices,
    }
    return render(request, template, context)


@login_required()
@require_http_methods(["GET"])
def suggest_alternative_animal_modal(request, awg_id, application_id):
    awg: Awg = get_object_or_404(Awg, pk=awg_id)
    context = check_awg_user_permissions_update_context(
        request, awg, ["MANAGE_APPLICATIONS"]
    )
    application: FosterApplication = get_object_or_404(
        FosterApplication, id=application_id, animal__awg=awg
    )

    context = {
        **context,
        "awg": awg,
        "app": application,
        "animals": awg.animals.all(),
    }

    return render(
        request,
        "awg/manage/applications/suggest_alternative_animal_modal.html",
        context,
    )


@login_required()
@require_http_methods(["POST"])
def suggest_alternative_animal_submit(request, awg_id, application_id):
    awg: Awg = get_object_or_404(Awg, pk=awg_id)
    context = check_awg_user_permissions_update_context(
        request, awg, ["MANAGE_APPLICATIONS"]
    )
    application: FosterApplication = get_object_or_404(
        FosterApplication, id=application_id, animal__awg=awg
    )
    animal = get_object_or_404(Animal, pk=request.POST["suggest-animal"], awg_id=awg.id)

    suggested_animal = FosterApplicationAnimalSuggestion(
        application=application,
        animal=animal,
    )
    suggested_animal.save()

    notify_caim_of_animal_suggestion(suggested_animal)

    context = {
        **context,
        "awg": awg,
        "app": application,
        "animal": animal,
    }

    return render(
        request,
        "awg/manage/applications/suggest_alternative_animal_submitted_modal.html",
        context,
    )
