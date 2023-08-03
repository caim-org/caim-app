import io
import logging
import os
from unicodedata import category

from click import style
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit, Field
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm, RadioSelect, formset_factory
from django.forms.models import model_to_dict
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from weasyprint import CSS, HTML

from caim_base.models.awg import Awg, AwgMember

from ..models.fosterer import FostererProfile, User
from ..notifications import notify_new_fosterer_profile

from django import forms
from ..models import FostererExistingPetDetail, FostererReferenceDetail, TypeOfAnimals


class ExistingPetDetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

    type_of_animals = forms.MultipleChoiceField(
        choices=TypeOfAnimals.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = FostererExistingPetDetail
        fields = [
            "name",
            "type_of_animals",
            "breed",
            "sex",
            "age",
            "weight_lbs",
            "spayed_neutered",
            "up_to_date_shots",
            "quirks",
        ]


class ReferenceDetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = FostererReferenceDetail
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "relation",
        ]
        required = (
            "first_name",
            "last_name",
            "email",
            "relation",
        )


class FostererProfileStage1Form(ModelForm):
    def __init__(self, *args, **kwargs):

        # patch user and profile info into "initial" to prefill fields
        initial_args = kwargs.get("initial", {})

        user_profile = None

        fosterer_profile = kwargs.get("instance")
        if fosterer_profile:
            user = fosterer_profile.user
            user_profile = user.userprofile

        if user_profile is not None:
            initial_args["firstname"] = user.first_name
            initial_args["lastname"] = user.last_name
            initial_args["city"] = user_profile.city
            initial_args["state"] = user_profile.state
            initial_args["zip_code"] = user_profile.zip_code

            kwargs["initial"] = initial_args

        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            if field in self.fields:
                self.fields[field].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "About you",
                'firstname',
                "lastname",
                "age",
                "email",
                "phone",
                "street_address",
                "city",
                "state",
                "zip_code",
            ),
            Submit("submit", "Save and continue", css_class="button"),
        )

    class Meta:
        model = FostererProfile
        fields = [
            "firstname",
            "lastname",
            "age",
            "email",
            "phone",
            "street_address",
            "city",
            "state",
            "zip_code",
        ]
        labels = {
            'firstname': 'First name',
            'lastname': 'Last name',
        }
        required = (
            "firstname",
            "lastname",
            "email",
            "phone",
            "street_address",
            "city",
            "state",
            "zip_code",
        )


class FostererProfileStage2Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            if field in self.fields:
                self.fields[field].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Animal preferences",
                "type_of_animals",
                "category_of_animals",
                "dog_size",
                "behavioural_attributes",
                "medical_issues",
                "special_needs",
                "behavioral_issues",
                "timeframe",
            ),
            Submit("submit", "Save and continue &raquo;", css_class="btn btn-primary"),
        )

    class Meta:
        model = FostererProfile
        fields = [
            "type_of_animals",
            "category_of_animals",
            "dog_size",
            "behavioural_attributes",
            "medical_issues",
            "special_needs",
            "behavioral_issues",
            "timeframe",
        ]
        required = (
            "type_of_animals",
            "category_of_animals",
            "timeframe",
        )
        widgets = {
            "timeframe": RadioSelect(),
        }


class FostererProfileStage3Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            if field in self.fields:
                self.fields[field].required = True

        self.fields["num_existing_pets"].widget.attrs.update(
            {
                "id": "num_existing_pets",
            }
        )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Pet Experience",
                "num_existing_pets",
                "experience_given_up_pet",
                "experience_description",
                "experience_categories",
            ),
            Submit(
                "submit_prev", "&laquo; Previous page", css_class="btn btn-secondary"
            ),
            Submit("submit", "Save and continue &raquo;", css_class="btn btn-primary"),
        )
        self.helper = FormHelper(self)

    class Meta:
        model = FostererProfile
        fields = [
            "num_existing_pets",
            "experience_given_up_pet",
            "experience_description",
            "experience_categories",
        ]
        required = (
            "num_existing_pets",
            "experience_given_up_pet",
            "experience_description",
            "experience_categories",
        )


class FostererProfileStage4Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            if field in self.fields:
                self.fields[field].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "References",
            ),
            Submit(
                "submit_prev", "&laquo; Previous page", css_class="btn btn-secondary"
            ),
            Submit("submit", "Save and continue &raquo;", css_class="btn btn-primary"),
        )

    class Meta:
        model = FostererProfile
        fields = []
        required = ()


class FostererProfileStage5Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            if field in self.fields:
                self.fields[field].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Household Details",
                "num_people_in_home",
                "people_in_home_detail",
                "yard_type",
                "yard_fence_over_5ft",
                "rent_own",
                "rent_restrictions",
                "hours_alone_description",
                "hours_alone_location",
                "sleep_location",
            ),
            Submit(
                "submit_prev", "&laquo; Previous page", css_class="btn btn-secondary"
            ),
            Submit("submit", "Save and continue &raquo;", css_class="btn btn-primary"),
        )

    class Meta:
        model = FostererProfile
        fields = [
            "num_people_in_home",
            "people_in_home_detail",
            "yard_type",
            "yard_fence_over_5ft",
            "rent_own",
            "rent_restrictions",
            "landlord_contact_text",
            "hours_alone_description",
            "hours_alone_location",
            "sleep_location",
        ]
        required = (
            "num_people_in_home",
            "yard_type",
            "rent_own",
            "hours_alone_description",
            "hours_alone_location",
            "sleep_location",
        )
        widgets = {
            "yard_type": RadioSelect(),
            "yard_fence_over_5ft": RadioSelect(),
            "rent_own": RadioSelect(),
        }


class FostererProfileStage6Form(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            if field in self.fields:
                self.fields[field].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Final thoughts",
                "other_info",
                "ever_been_convicted_abuse",
                "agree_share_details",
                "agree_social_media",
            ),
            Submit(
                "submit_prev", "&laquo; Previous page", css_class="btn btn-secondary"
            ),
            Submit("submit", "Save and continue &raquo;", css_class="btn btn-primary"),
        )

    class Meta:
        model = FostererProfile
        fields = [
            "other_info",
            "ever_been_convicted_abuse",
            "agree_share_details",
            "agree_social_media",
        ]
        required = (
            "ever_been_convicted_abuse",
            "agree_share_details",
            "agree_social_media",
        )
        widgets = {
            "ever_been_convicted_abuse": RadioSelect(),
            "agree_share_details": RadioSelect(),
            "agree_social_media": RadioSelect(),
        }


STAGES = {
    "about-you": {
        "number": 1,
        "form_class": FostererProfileStage1Form,
        "next": "animal-preferences",
        "prev": None,
    },
    "animal-preferences": {
        "number": 2,
        "form_class": FostererProfileStage2Form,
        "next": "pet-experience",
        "prev": "about-you",
    },
    "pet-experience": {
        "number": 3,
        "form_class": FostererProfileStage3Form,
        "next": "references",
        "prev": "animal-preferences",
    },
    "references": {
        "number": 4,
        "form_class": FostererProfileStage4Form,
        "next": "household-details",
        "prev": "pet-experience",
    },
    "household-details": {
        "number": 5,
        "form_class": FostererProfileStage5Form,
        "next": "final-thoughts",
        "prev": "references",
    },
    "final-thoughts": {
        "number": 6,
        "form_class": FostererProfileStage6Form,
        "next": "complete",
        "prev": "household-details",
    },
}


@login_required()
@require_http_methods(["GET"])
def start(request):
    return redirect("/fosterer/about-you")


@login_required()
@require_http_methods(["POST", "GET"])
def edit(request, stage_id):
    user = request.user

    try:
        fosterer_profile = FostererProfile.objects.get(user=user)
    except FostererProfile.DoesNotExist:
        # Create a blank profile for this user
        fosterer_profile = FostererProfile(user=user)
        fosterer_profile.email = user.email
        fosterer_profile.save()

    if stage_id == "complete":
        if not fosterer_profile.is_complete:
            # @todo check if all fields done
            fosterer_profile.is_complete = True
            fosterer_profile.save()
            notify_new_fosterer_profile(fosterer_profile)
        return render(
            request,
            "fosterer_profile/complete.html",
            {
                "user": user,
                "pageTitle": "Fosterer profile complete",
            },
        )

    if not stage_id in STAGES:
        raise Http404("Stage not found")

    stage = STAGES[stage_id]
    stage_number = stage["number"]
    form_class = stage["form_class"]
    next_stage = stage["next"]
    prev_stage = stage["prev"]

    if request.method == "POST":
        ExistingPetDetailFormSet = formset_factory(ExistingPetDetailForm, extra=3)
        ReferenceDetailFormSet = formset_factory(
            ReferenceDetailForm, extra=3, min_num=3, validate_min=True
        )

        form = form_class(request.POST, instance=fosterer_profile)
        existing_pet_detail_formset = ExistingPetDetailFormSet(
            request.POST, prefix="existingpetdetail"
        )
        reference_detail_formset = ReferenceDetailFormSet(
            request.POST, prefix="referencedetail"
        )

        formsets_are_valid = True

        if stage_id == "pet-experience":
            if not existing_pet_detail_formset.is_valid():
                formsets_are_valid = False

        if stage_id == "references":
            if not reference_detail_formset.is_valid():
                formsets_are_valid = False

        form_is_valid = form.is_valid()

        if form_is_valid and formsets_are_valid:
            form.save()

            if stage_id == "pet-experience":
                # limit to 3 saved existing pets (for now). do not duplicate
                existing_pet_details = FostererExistingPetDetail.objects.filter(
                    fosterer_profile=fosterer_profile
                ).order_by("id")

                for index, detail_form in enumerate(existing_pet_detail_formset):
                    if detail_form.is_valid():
                        detail_data = detail_form.cleaned_data
                        if index < len(existing_pet_details):
                            existing_detail = existing_pet_details[index]
                            existing_detail.name = detail_data.get("name")
                            existing_detail.type_of_animals = detail_data.get(
                                "type_of_animals"
                            )
                            existing_detail.breed = detail_data.get("breed")
                            existing_detail.sex = detail_data.get("sex")
                            existing_detail.age = detail_data.get("age")
                            existing_detail.weight_lbs = detail_data.get("weight_lbs")
                            existing_detail.spayed_neutered = detail_data.get(
                                "spayed_neutered"
                            )
                            existing_detail.up_to_date_shots = detail_data.get(
                                "up_to_date_shots"
                            )
                            existing_detail.quirks = detail_data.get("quirks")
                            existing_detail.save()
                        else:
                            FostererExistingPetDetail.objects.create(
                                fosterer_profile=fosterer_profile,
                                name=detail_data.get("name"),
                                type_of_animals=detail_data.get("type_of_animals"),
                                breed=detail_data.get("breed"),
                                sex=detail_data.get("sex"),
                                age=detail_data.get("age"),
                                weight_lbs=detail_data.get("weight_lbs"),
                                spayed_neutered=detail_data.get("spayed_neutered"),
                                up_to_date_shots=detail_data.get("up_to_date_shots"),
                                quirks=detail_data.get("quirks"),
                            )

            if stage_id == "references":
                existing_references = FostererReferenceDetail.objects.filter(
                    fosterer_profile=fosterer_profile
                ).order_by("id")

                for index, detail_form in enumerate(reference_detail_formset):
                    # do not attempt to save empty forms
                    if detail_form.is_valid() and detail_form.has_changed():
                        detail_data = detail_form.cleaned_data
                        if index < len(existing_references):
                            existing_detail = existing_references[index]
                            existing_detail.first_name = detail_data.get("first_name")
                            existing_detail.last_name = detail_data.get("last_name")
                            existing_detail.email = detail_data.get("email")
                            existing_detail.phone = detail_data.get("phone")
                            existing_detail.relation = detail_data.get("relation")
                            existing_detail.save()
                        else:
                            FostererReferenceDetail.objects.create(
                                fosterer_profile=fosterer_profile,
                                first_name=detail_data.get("first_name"),
                                last_name=detail_data.get("last_name"),
                                email=detail_data.get("email"),
                                phone=detail_data.get("phone"),
                                relation=detail_data.get("relation"),
                            )

            is_previous = "submit_prev" in request.POST
            if is_previous:
                return redirect(f"/fosterer/{prev_stage}")
            else:
                return redirect(f"/fosterer/{next_stage}")

        else:
            messages.error(request, "Please correct form errors")
    else:
        form = form_class(instance=fosterer_profile)

        existing_pets = FostererExistingPetDetail.objects.filter(
            fosterer_profile=fosterer_profile
        )
        num_existing_pets = existing_pets.count()
        extra_forms_needed = max(0, 6 - num_existing_pets)
        ExistingPetDetailFormSet = formset_factory(
            ExistingPetDetailForm, extra=extra_forms_needed
        )
        existing_pet_data = [model_to_dict(pet) for pet in existing_pets]
        existing_pet_detail_formset = ExistingPetDetailFormSet(
            prefix="existingpetdetail", initial=existing_pet_data
        )

        references = FostererReferenceDetail.objects.filter(
            fosterer_profile=fosterer_profile
        )
        num_references = references.count()
        extra_forms_needed = max(0, 3 - num_references)
        ReferenceDetailFormSet = formset_factory(
            ReferenceDetailForm, extra=extra_forms_needed, validate_min=True
        )
        references_data = [model_to_dict(person) for person in references]
        reference_detail_formset = ReferenceDetailFormSet(
            prefix="referencedetail", initial=references_data
        )

    return render(
        request,
        "fosterer_profile/edit.html",
        {
            "user": user,
            "form": form,
            "existing_pet_detail_formset": existing_pet_detail_formset,
            "reference_detail_formset": reference_detail_formset,
            "pageTitle": "Edit your fosterer profile",
            "stageNumber": stage_number,
            "stage_id": stage_id,
        },
    )


@login_required()
def download_fosterer_profile(request: HttpRequest, fosterer_id: int) -> HttpResponse:
    user = request.user
    awg_member: AwgMember = AwgMember.objects.filter(user=user).first()
    if not awg_member:
        raise PermissionDenied("You are not a member of an AWG")

    awg: Awg = awg_member.awg

    if not awg.status == "PUBLISHED":
        raise PermissionDenied("Your AWG is not published")

    fosterer: FostererProfile = get_object_or_404(FostererProfile, pk=fosterer_id)
    animal_type_labels = []
    if fosterer.type_of_animals:
        animal_type_labels = [
            TypeOfAnimals(animal_type).label
            for animal_type in fosterer.type_of_animals
        ]

    category_of_animals_labels = []
    if fosterer.category_of_animals:
        category_of_animals_labels = [
            fosterer.CategoryOfAnimals(category).label
            for category in fosterer.category_of_animals
        ]

    behaviour_labels = []
    if fosterer.behavioural_attributes:
        for behaviour in fosterer.behavioural_attributes:
            try:
                fosterer.BehaviouralAttributes(behaviour)
                behaviour_labels.append(fosterer.BehaviouralAttributes(behaviour).label)
            except:
                logging.warning("Could not find behavioral attribute: %s"  % behaviour)

    experience_categories_labels = []
    if fosterer.experience_categories:
        experience_categories_labels = [
            fosterer.ExperienceCategories(experience).label
            for experience in fosterer.experience_categories
        ]

    context = {
        "fosterer": fosterer,
        "animal_type_labels": animal_type_labels,
        "category_of_animals_labels": category_of_animals_labels,
        "behaviour_labels": behaviour_labels,
        "experience_categories_labels": experience_categories_labels,
    }

    pdf_string = render_to_string("fosterer_profile/pdf.html", context, request)
    pdf_file = HTML(string=pdf_string).write_pdf(
        stylesheets=[
            CSS(string="@page { size: letter portrait; margin: 1cm }"),
            CSS(filename=os.path.join(settings.STATIC_ROOT, "css/normalize.css")),
            CSS(filename=os.path.join(settings.STATIC_ROOT, "css/pdf.css")),
        ]
    )

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f"filename=fosterer-profile-{fosterer_id}.pdf"
    return response
