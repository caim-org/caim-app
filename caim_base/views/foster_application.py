import logging
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from weasyprint import CSS, HTML

from ..models import TypeOfAnimals
from ..models.animals import Animal
from ..models.awg import Awg, AwgMember
from ..models.fosterer import (
    FosterApplication,
    FostererExistingPetDetail,
    FostererPersonInHomeDetail,
    FostererProfile,
    FostererReferenceDetail,
)


@login_required()
@require_http_methods(["POST", "GET"])
def application(request):
    user = request.user

    # check if person has completed fosterer profile. if not send to fill.
    try:
        fosterer_profile = FostererProfile.objects.get(user=user)
    except FostererProfile.DoesNotExist:
        return redirect("/foster")

    if not fosterer_profile.is_complete:
        return redirect("/foster")

    if request.method == "POST":
        animal_id = request.POST.get("animal_id")

        try:
            animal = Animal.objects.get(pk=animal_id)
        except Animal.DoesNotExist as e:
            raise Http404("No Animal matches the given query.") from e

        # check if application exists already
        try:
            FosterApplication.objects.get(fosterer=fosterer_profile, animal=animal)
            return render(
                request,
                "foster_application/exists.html",
                {
                    "user": user,
                    "pageTitle": "Foster application already exists",
                },
            )
        except FosterApplication.DoesNotExist:
            pass

        application = FosterApplication(
            fosterer=fosterer_profile,
            animal=animal,
            status=FosterApplication.Statuses.PENDING,
            reject_reason_detail=None,
        )

        application.save()

        return render(
            request,
            "foster_application/complete.html",
            {
                "user": user,
                "pageTitle": "Foster application complete",
            },
        )

    else:
        # GET method expects animal_id in query string
        animal_id = request.GET.get("animal_id", None)
        animal = get_object_or_404(Animal, pk=animal_id)

    return render(
        request,
        "foster_application/application.html",
        {
            "user": user,
            "animal": animal,
            "fosterer_profile": fosterer_profile,
            "pageTitle": "Foster Application",
        },
    )


@login_required()
def download_foster_application(request: HttpRequest) -> HttpResponse:
    fosterer_id = request.GET.get("fosterer_id", None)
    animal_id = request.GET.get("animal_id", None)

    user = request.user
    awg_member = AwgMember.objects.filter(user=user).first()
    if not awg_member:
        raise PermissionDenied("You are not a member of an AWG")

    awg: Awg = awg_member.awg

    if not awg.status == "PUBLISHED":
        raise PermissionDenied("Your AWG is not published")

    fosterer: FostererProfile = get_object_or_404(FostererProfile, pk=fosterer_id)
    animal: Animal = get_object_or_404(Animal, pk=animal_id)
    foster_application: FosterApplication = get_object_or_404(
        FosterApplication, fosterer=fosterer, animal=animal
    )

    existing_animals: QuerySet[
        FostererExistingPetDetail
    ] = FostererExistingPetDetail.objects.filter(fosterer_profile=fosterer)
    references: QuerySet[
        FostererReferenceDetail
    ] = FostererReferenceDetail.objects.filter(fosterer_profile=fosterer)
    people_in_home: QuerySet[
        FostererPersonInHomeDetail
    ] = FostererPersonInHomeDetail.objects.filter(fosterer_profile=fosterer)

    animal_type_labels = []
    if fosterer.type_of_animals:
        animal_type_labels = [
            TypeOfAnimals(animal_type).label for animal_type in fosterer.type_of_animals
        ]

    category_of_animals_labels = []
    if fosterer.category_of_animals:
        category_of_animals_labels = [
            fosterer.CategoryOfAnimals(category).label
            for category in fosterer.category_of_animals
        ]

    dog_size_labels = []
    if fosterer.dog_size:
        dog_size_labels = [
            fosterer.DogSize(dog_size).label for dog_size in fosterer.dog_size
        ]

    behaviour_labels = []
    if fosterer.behavioural_attributes:
        behaviour_labels = [
            fosterer.BehaviouralAttributes(behaviour).label
            for behaviour in fosterer.behavioural_attributes
        ]

    experience_categories_labels = []
    if fosterer.experience_categories:
        experience_categories_labels = [
            fosterer.ExperienceCategories(experience).label
            for experience in fosterer.experience_categories
        ]

    context = {
        "application": foster_application,
        "existing_animals": existing_animals,
        "references": references,
        "people_in_home": people_in_home,
        "animal_type_labels": animal_type_labels,
        "dog_size_labels": dog_size_labels,
        "category_of_animals_labels": category_of_animals_labels,
        "behaviour_labels": behaviour_labels,
        "experience_categories_labels": experience_categories_labels,
    }

    pdf_string = render_to_string("fosterer_profile/pdf.html", context, request)
    pdf_file = HTML(string=pdf_string).write_pdf(
        stylesheets=[
            CSS(string="@page { size: letter portrait; margin: 1cm }"),
            CSS(filename=os.path.join(settings.STATIC_ROOT, "vendor/normalize.css")),
            CSS(filename=os.path.join(settings.STATIC_ROOT, "css/pdf.css")),
        ]
    )

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f"filename=fosterer-profile-{fosterer_id}.pdf"
    for a in existing_animals:
        logging.info("animal spayed_neutered is %s", a.spayed_neutered)
    return response
