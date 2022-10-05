from django.core.exceptions import BadRequest, PermissionDenied
from django.http import Http404
from django.shortcuts import render, redirect
from django import forms
from django.core import validators
from ..models import User, UserProfile


class UserProfileForm(forms.Form):
    username = forms.CharField(
        label="Display name",
        help_text="Your name as you want it to appear on the site. This will be visible publicly.",
        max_length=30,
        required=True,
        validators=[
            validators.RegexValidator(
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
    description = forms.CharField(
        label="Introduction",
        help_text="Tell us about yourself. This will be visible publicly.",
        widget=forms.Textarea,
        required=False,
    )


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
            initial={"username": user.username, "description": user_profile.description}
        )

    return render(request, "user_profile/edit.html", {"user": user, "form": form})


def my_organizations(request):
    memberships = request.user.awgmember_set.all()
    return render(
        request,
        "user_profile/my_organizations.html",
        {"memberships": memberships, "pageTitle": "My organizations"},
    )
