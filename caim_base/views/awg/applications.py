from textwrap import dedent
from typing import Optional, Tuple

from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from caim_base.models.awg import Awg
from caim_base.models.fosterer import FosterApplication
from caim_base.views.awg.user_permissions import \
    check_awg_user_permissions_update_context


def query_applications_for_awg(
    awg: Awg, order_by: Optional[Tuple[str]] = None, status: Optional[str] = None
) -> QuerySet:
    applications = FosterApplication.objects.select_related("animal").filter(animal__awg=awg)
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
        "application_status_options": [c[0] for c in FosterApplication.FosterApplicationStatus.choices],
    }
    context = check_awg_user_permissions_update_context(request, awg, ["MANAGE_APPLICATIONS"], context)
    return render(request, "awg/manage/applications/list.html", context)


@login_required()
@require_http_methods(["POST"])
def update_application(request, awg_id, application_id):
    awg = get_object_or_404(Awg, pk=awg_id)

    application: FosterApplication = get_object_or_404(FosterApplication, id=application_id, animal__awg=awg)
    new_status = request.POST.get("status")
    if new_status is not None:
        # this is lame is there any better way to do this
        if new_status.upper() not in [t[0] for t in FosterApplication.FosterApplicationStatus.choices]:
            return HttpResponse(
                dedent(
                    f"""
                    <h1>400 Invalid</h1>
                    <div>Invalid POST parameter "status": {new_status}</div>
                    <div>Valid Options:{FosterApplication.FosterApplicationStatus.choices}</div>
                """
                ),
                status=400,
            )
        application.status = new_status.upper()
    application.reject_reason = request.POST.get("reject_reason")
    application.save()

    current_user_permissions = awg.get_permissions_for_user(request.user)
    context = {
        "awg": awg,
        "applications": query_applications_for_awg(awg),
        "application_status_options": [c[0] for c in FosterApplication.FosterApplicationStatus.choices],
    }
    context = check_awg_user_permissions_update_context(request, awg, ["MANAGE_APPLICATIONS"], context)
    return render(request, "awg/manage/applications/list.html", context)


@login_required()
@require_http_methods(["GET"])
def update_application_status_modal(request, awg_id, application_id, status):
    awg = get_object_or_404(Awg, pk=awg_id)
    _ = check_awg_user_permissions_update_context(request, awg, ["MANAGE_APPLICATIONS"])
    application: FosterApplication = get_object_or_404(FosterApplication, id=application_id, animal__awg=awg)

    templates = {
        FosterApplication.FosterApplicationStatus.ACCEPTED: "awg/manage/applications/accept_modal.html",
        FosterApplication.FosterApplicationStatus.REJECTED: "awg/manage/applications/reject_modal.html",
        FosterApplication.FosterApplicationStatus.PENDING: "awg/manage/applications/pend_modal.html",
    }
    template = templates[status]

    context = {
        "awg": awg,
        "app": application,
    }
    return render(request, template, context)
