from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied, BadRequest
from django.http import Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from caim_base.views.awg.user_permissions import check_awg_user_permissions_update_context

from ...models.awg import Awg, User, AwgMember

@login_required()
@require_http_methods(["GET"])
def list_members(request, awg_id):
    awg = get_object_or_404(Awg, pk=awg_id)

    members = awg.awgmember_set.all()

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name} | Manage members",
        "members": members,
    }
    context = check_awg_user_permissions_update_context(request, awg, ["MANAGE_MEMBERS"], context)
    return render(request, "awg/manage/members/list.html", context)


@login_required()
@require_http_methods(["POST"])
def add_member(request, awg_id):
    awg = get_object_or_404(Awg, pk=awg_id)
    _ = check_awg_user_permissions_update_context(request, awg, ["MANAGE_MEMBERS"])

    try:
        email = request.POST.get("email")
        canEditProfile = "canEditProfile" in request.POST
        canManageAnimals = "canManageAnimals" in request.POST
        canManageMembers = "canManageMembers" in request.POST
        if not email:
            raise BadRequest("Missing email address parameter")

        if not (canEditProfile or canManageAnimals or canManageMembers):
            raise BadRequest("Must have at least 1 permission")

        # Lowercase to avoid case sensitivity
        email = email.lower()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise BadRequest("User does not exist")

        existing_member = AwgMember.objects.filter(awg=awg, user=user).all()
        if existing_member:
            raise BadRequest("User is already a member of this AWG")

        member = AwgMember(
            user=user,
            awg=awg,
            canEditProfile=canEditProfile,
            canManageAnimals=canManageAnimals,
            canManageMembers=canManageMembers,
        )
        member.save()
        messages.success(request, "Member was added to this organization")
    except BadRequest as e:
        messages.error(request, "Could not add member: " + str(e))

    return redirect(f"{awg.get_absolute_url()}/members")


@login_required()
@require_http_methods(["POST"])
def update_member(request, awg_id):
    awg = get_object_or_404(Awg, pk=awg_id)
    _ = check_awg_user_permissions_update_context(request, awg, ["MANAGE_MEMBERS"])
    member_id = request.POST["membershipId"]
    action = request.POST["action"]

    try:
        try:
            member = AwgMember.objects.get(id=member_id)
        except AwgMember.DoesNotExist:
            raise BadRequest("Member not found")

        if action == "DELETE":
            member.delete()
            messages.success(request, "Member was removed from this organization")
        elif action == "UPDATE":
            member.canEditProfile = "canEditProfile" in request.POST
            member.canManageAnimals = "canManageAnimals" in request.POST
            member.canManageMembers = "canManageMembers" in request.POST
            member.save()
            messages.success(request, "Member was update for this organization")
        else:
            raise BadRequest("Unknown action")

    except BadRequest as e:
        messages.error(request, "Could not modify member: " + str(e))

    return redirect(f"{awg.get_absolute_url()}/members")
