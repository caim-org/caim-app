from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied, BadRequest
from django.http import Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from ...models.awg import Awg, User, AwgMember


def check_awg_user_permissions(request, awg_id):
    try:
        awg = Awg.objects.get(id=awg_id)
    except Awg.DoesNotExist:
        raise Http404("Awg not found")

    current_user_permissions = awg.get_permissions_for_user(request.user)
    if not "MANAGE_MEMBERS" in current_user_permissions:
        raise PermissionDenied(
            "User does not have permission to manage members for this AWG"
        )
    return awg, current_user_permissions


@login_required()
@require_http_methods(["GET"])
def list_members(request, awg_id):
    awg, current_user_permissions = check_awg_user_permissions(request, awg_id)

    members = awg.awgmember_set.all()

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name} | Manage members",
        "currentUserPermissions": current_user_permissions,
        "members": members,
    }
    return render(request, "awg/manage/members/list.html", context)


@login_required()
@require_http_methods(["POST"])
def add_member(request, awg_id):
    awg, current_user_permissions = check_awg_user_permissions(request, awg_id)

    try:
        email = request.POST.get("email")
        canEditProfile = "canEditProfile" in request.POST
        canManageAnimals = "canManageAnimals" in request.POST
        canManageMembers = "canManageMembers" in request.POST
        if not email:
            raise BadRequest("Missing email address parameter")

        if not (canEditProfile or canManageAnimals or canManageMembers):
            raise BadRequest("Must have at least 1 permission")

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
    awg, current_user_permissions = check_awg_user_permissions(request, awg_id)
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
