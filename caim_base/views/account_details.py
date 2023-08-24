from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.conf import settings

from ..forms import zip_validator
from ..models.user import UserProfile
from ..states import form_states
from ..utils import salesforce


class UserDetailsForm(forms.Form):
    first_name = forms.CharField(label="First name")
    last_name = forms.CharField(label="Last name")
    city = forms.CharField(label="City", max_length=32)
    state = forms.ChoiceField(choices=form_states.items())
    zip_code = forms.CharField(label="ZIP Code", validators=[zip_validator])


@login_required
@require_http_methods(["GET"])
def view(request: HttpRequest) -> HttpResponse:
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile is None:
        # Create a blank profile for this user
        user_profile = UserProfile(user=request.user)
        user_profile.save()

    return render(
        request,
        "account_details/view.html",
        {
            "user_profile": user_profile,
            "pageTitle": f"{request.user.username} | Account details",  # type: ignore
        },
    )


@login_required
@require_http_methods(["POST", "GET"])
def edit(request: HttpRequest) -> HttpResponse:
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile is None:
        # Create a blank profile for this user
        user_profile = UserProfile(user=request.user)
        user_profile.save()

    user = request.user

    if request.method == "POST":
        form = UserDetailsForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"]  # type: ignore
            user.last_name = form.cleaned_data["last_name"]  # type: ignore
            user.save()

            user_profile.city = form.cleaned_data["city"]
            user_profile.state = form.cleaned_data["state"]
            user_profile.zip_code = form.cleaned_data["zip_code"]
            user_profile.save()

            # create or update salesforce contact
            if settings.SALESFORCE_ENABLED:
                if user_profile.salesforce_id is not None:
                    salesforce.update_contact(user_profile.salesforce_id, form)
                else:
                    salesforce.create_contact(user_profile, form)

            return redirect("account_details")

    form = UserDetailsForm(
        initial={
            "first_name": user.first_name,  # type: ignore
            "last_name": user.last_name,  # type: ignore
            "city": user_profile.city,
            "state": user_profile.state,
            "zip_code": user_profile.zip_code,
        }
    )

    return render(
        request,
        "account_details/edit.html",
        {
            "user_profile": user_profile,
            "form": form,
            "pageTitle": f"{user.username} | Edit account details",  # type: ignore
        },
    )
