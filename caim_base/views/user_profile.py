from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.validators import RegexValidator
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ..forms import zip_validator
from ..models.user import User, UserProfile
from ..states import form_states


class UserProfileForm(forms.Form):
    username = forms.CharField(
        label="Display name",
        help_text="Your name as you want it to appear on the site. This will be visible publicly.",
        max_length=30,
        required=True,
        validators=[
            RegexValidator(
                r"^[\w.@+-]+$",
                (
                    "Enter a valid username. "
                    "This value may contain only letters, numbers "
                    "and @/./+/-/_ characters."
                ),
                "invalid",
            ),
        ],
    )
    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last name")
    city = forms.CharField(label="City", max_length=32)
    state = forms.ChoiceField(choices=form_states.items())
    zip_code = forms.CharField(label="ZIP Code", validators=[zip_validator])
    description = forms.CharField(
        label="Introduction",
        help_text="Tell us about yourself. This will be visible publicly.",
        widget=forms.Textarea,
        required=False,
    )


@require_http_methods(["GET"])
def view(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User not found")

    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # Create a blank profile for this user
        user_profile = UserProfile(user=user)
        user_profile.save()

    return render(
        request,
        "user_profile/view.html",
        {
            "user": user,
            "user_profile": user_profile,
            "pageTitle": f"{user.username} | User profile",
        },
    )


@login_required()
@require_http_methods(["POST", "GET"])
def edit(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User not found")

    if user != request.user and not request.user.is_staff:
        raise PermissionDenied("User does not have permission to edit this user")

    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        # Create a blank profile for this user
        user_profile = UserProfile(user=user)
        user_profile.save()

    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user.username = form.cleaned_data["username"]
            user.save()

            user_profile.description = form.cleaned_data["description"]
            user_profile.save()

            return redirect(f"/user/{user.username}")
    else:
        form = UserProfileForm(
            initial={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "city": user_profile.city,
                "state": user_profile.state,
                "zip_code": user_profile.zip_code,
                "description": user_profile.description
            }
        )

    return render(
        request,
        "user_profile/edit.html",
        {"user": user, "form": form, "pageTitle": "Edit your user profile"},
    )


@login_required()
@require_http_methods(["GET"])
def my_organizations(request):
    memberships = request.user.awgmember_set.all()
    return render(
        request,
        "user_profile/my_organizations.html",
        {"memberships": memberships, "pageTitle": "My organizations"},
    )
