from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm, RadioSelect
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

from ..models.fosterer import FostererProfile, FostererApplication

@login_required()
@require_http_methods(["POST", "GET"])
def application(request, stage_id):
    user = request.user

    if request.method == "POST":
        form = form_class(request.POST, instance=fosterer_profile)

        animal 


        #if form.is_valid():
            #fosterer_profile = form.save()
        else:
            messages.error(request, "Please correct form errors")
    else:
        # check if person has completed fosterer profile. if not send to fill.
        try:
            fosterer_profile = FostererProfile.objects.get(user=user)
        except FostererProfile.DoesNotExist:
            return redirect('/fosterer')

        if not forster_profile.is_complete:
            return redirect('/fosterer')

        #GET method expects animal_id in query string
        animal_id = request.GET.get('animal_id', None)
        animal = get_object_or_404(Animal, pk=animal_id)

    return render(
        request,
        "fosterer_profile/application.html",
        {
            "user": user,
            "animal": user,
            "foster_profile": foster_profile,
            "pageTitle": "Foster Application",
        },
    )
