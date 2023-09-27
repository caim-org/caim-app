from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from ..forms import NewUserForm
from ..models import UserProfile, FostererProfile
from ..utils import salesforce

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            # Lowercase to avoid case sensitivity (email address)
            username = username.lower()
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect(request.GET.get("next", "home"))
            messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    if request.user.is_authenticated:
        return redirect("home")

    return render(
        request=request,
        template_name="auth/login.html",
        context={
            "login_form": form,
            "pageTitle": "Login",
        },
    )


def register_view(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            zip_code = form.cleaned_data.get("zip_code")
            city = form.cleaned_data.get("city")
            state = form.cleaned_data.get("state")
            user_profile = UserProfile(
                user=user, zip_code=zip_code, city=city, state=state
            )
            user_profile.save()

            salesforce.create_or_update_contact(user_profile)

            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect(request.GET.get("next", "register_success"))
        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = NewUserForm()

    if request.user.is_authenticated:
        return redirect("register_success")

    return render(
        request=request,
        template_name="auth/register.html",
        context={
            "register_form": form,
            "pageTitle": "Register",
        },
    )


def register_success(request):
    """Afer signup propmt user to fill foster profile or view AWG info"""
    fosterer_profile = FostererProfile(user=request.user)

    if fosterer_profile is None or not fosterer_profile.is_complete:
        return render(
            request=request,
            template_name="auth/register_success.html",
        )
    else:
        return redirect("home")


def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("home")
