from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, RadioSelect, formset_factory
from django.forms.models import model_to_dict
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from django.views.decorators.http import require_http_methods


from ..models import (
    FostererExistingPetDetail,
    FostererPersonInHomeDetail,
    FostererReferenceDetail,
)
from ..models.fosterer import FostererProfile
from ..models.user import UserProfile
from ..notifications import notify_new_fosterer_profile


class ExistingPetDetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = FostererExistingPetDetail
        fields = [
            "name",
            "type_of_animal",
            "breed",
            "sex",
            "age",
            "weight_lbs",
            "spayed_neutered",
            "up_to_date_shots",
            "quirks",
        ]
        labels = {
            "type_of_animal": "Type",
        }


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
            "phone",
            "relation",
        )


class PersonInHomeDetailForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

    class Meta:
        model = FostererPersonInHomeDetail
        fields = [
            "name",
            "relation",
            "age",
            "email",
        ]
        required = ()


class FostererProfileStage1Form(ModelForm):
    def __init__(self, *args, **kwargs):
        # patch user and profile info into "initial" to prefill fields
        initial_args = kwargs.get("initial", {})

        user_profile = None

        fosterer_profile: FostererProfile | None = kwargs.get("instance")
        if fosterer_profile:
            user = fosterer_profile.user
            user_profile = UserProfile.objects.get(user=user)

            if user_profile is not None:
                if not fosterer_profile.firstname:
                    initial_args["firstname"] = user.first_name
                if not fosterer_profile.lastname:
                    initial_args["lastname"] = user.last_name
                if not fosterer_profile.city:
                    initial_args["city"] = user_profile.city
                if not fosterer_profile.state:
                    initial_args["state"] = user_profile.state
                if not fosterer_profile.zip_code:
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
                "firstname",
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
            "firstname": "First name",
            "lastname": "Last name",
        }
        required = (
            "firstname",
            "lastname",
            "age",
            "email",
            "age",
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
            "behavioural_attributes",
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
                "all_in_agreement",
                "pet_allergies",
                "stairs",
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
            "all_in_agreement",
            "pet_allergies",
            "stairs",
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
            "all_in_agreement",
            "pet_allergies",
            "stairs",
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
    after = request.GET.get('after', '')
    return redirect(f"/fosterer/about-you?after={after}")


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

        link = request.GET.get('after') or reverse('browse')
        return render(
            request,
            "fosterer_profile/complete.html",
            {
                "user": user,
                "link": link,
                "pageTitle": "Fosterer profile complete",
            },
        )

    if stage_id not in STAGES:
        raise Http404("Stage not found")

    stage = STAGES[stage_id]
    stage_number = stage["number"]
    form_class = stage["form_class"]
    next_stage = stage["next"]
    prev_stage = stage["prev"]

    if request.method == "POST":
        ExistingPetDetailFormSet = formset_factory(ExistingPetDetailForm, extra=6)
        ReferenceDetailFormSet = formset_factory(
            ReferenceDetailForm, extra=3, min_num=3, validate_min=True
        )
        PersonInHomeDetailFormSet = formset_factory(
            PersonInHomeDetailForm, extra=6, min_num=6
        )

        form = form_class(request.POST, instance=fosterer_profile)

        existing_pet_detail_formset = ExistingPetDetailFormSet(
            request.POST, prefix="existingpetdetail"
        )
        reference_detail_formset = ReferenceDetailFormSet(
            request.POST, prefix="referencedetail"
        )
        person_in_home_detail_formset = PersonInHomeDetailFormSet(
            request.POST, prefix="personinhomedetail"
        )

        formsets_are_valid = True

        if stage_id == "pet-experience":
            # Number of pet fields filled must be equal, or great then the listed number of pets.
            num_of_pets = int(existing_pet_detail_formset.data['num_existing_pets'])
            if num_of_pets:
                for index, existing_pet_detail_form in enumerate(existing_pet_detail_formset):
                    if index < num_of_pets:
                        existing_pet_detail_form.full_clean()
                        any_missing_fields = not all(value is not None for value in existing_pet_detail_form.cleaned_data.values())
                        if not existing_pet_detail_form.cleaned_data or any_missing_fields:
                            formsets_are_valid = False
                            messages.error(
                                request,
                                f"Ensure the \"Number of Pets\" ({num_of_pets}) matches the number of "
                                f"\"Pet Details\" sections you entirely have filled out."
                            )
                            break

            if not existing_pet_detail_formset.is_valid():
                formsets_are_valid = False

        if stage_id == "references":
            if not reference_detail_formset.is_valid():
                formsets_are_valid = False

        if stage_id == "household-details":
            # Number of cohabitant fields filled must be equal, or great then the listed number of people in the
            # home.
            num_people_in_home = int(person_in_home_detail_formset.data['num_people_in_home'])
            if num_people_in_home:
                for index, person_in_home_detail_form in enumerate(person_in_home_detail_formset):
                    if index < num_people_in_home:
                        person_in_home_detail_form.full_clean()
                        any_missing_fields = not all(value is not None for value in person_in_home_detail_form.cleaned_data.values())
                        if not person_in_home_detail_form.cleaned_data or any_missing_fields:
                            formsets_are_valid = False
                            messages.error(
                                request,
                                f"Ensure the number of people in your home ({num_people_in_home}) matches " \
                                f"the number of \"Person in Home Details\" sections you have entirely filled out."
                            )
                            break

            # Ensure if a user has selected `Rent` they must fill out rent details.
            rent_own = person_in_home_detail_formset.data['rent_own']
            if rent_own == FostererProfile.RentOwn.RENT:
                if not person_in_home_detail_formset.data['rent_restrictions']:
                    formsets_are_valid = False
                    messages.error(request, 'Please describe any pet restrictions that are in place.')
                if not person_in_home_detail_formset.data['landlord_contact_text']:
                    formsets_are_valid = False
                    messages.error(request, 'Please provide your landlord’s contact information below.')

            if not person_in_home_detail_formset.is_valid():
                formsets_are_valid = False

        form_is_valid = form.is_valid()

        if not formsets_are_valid:
            messages.error(request, "Please correct any form errors")

        if form_is_valid and formsets_are_valid:
            form.save()

            if stage_id == "pet-experience":
                # limit to 6 saved existing pets (for now). do not duplicate
                existing_pet_details = FostererExistingPetDetail.objects.filter(
                    fosterer_profile=fosterer_profile
                ).order_by("id")

                for index, detail_form in enumerate(existing_pet_detail_formset):
                    if detail_form.is_valid():
                        detail_data = detail_form.cleaned_data
                        if index < len(existing_pet_details):
                            existing_detail = existing_pet_details[index]
                            existing_detail.name = detail_data.get("name")
                            existing_detail.type_of_animal = detail_data.get(
                                "type_of_animal"
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
                            fields = [
                                "name",
                                "type_of_animal",
                                "breed",
                                "sex",
                                "age",
                                "weight_lbs",
                                "spayed_neutered",
                                "up_to_date_shots",
                                "quirks",
                            ]
                            if any(detail_data.get(field) for field in fields):
                                FostererExistingPetDetail.objects.create(
                                    fosterer_profile=fosterer_profile,
                                    name=detail_data.get("name"),
                                    type_of_animal=detail_data.get("type_of_animal"),
                                    breed=detail_data.get("breed"),
                                    sex=detail_data.get("sex"),
                                    age=detail_data.get("age"),
                                    weight_lbs=detail_data.get("weight_lbs"),
                                    spayed_neutered=detail_data.get("spayed_neutered"),
                                    up_to_date_shots=detail_data.get(
                                        "up_to_date_shots"
                                    ),
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

            # TODO handle these formsets in dedicated functions.
            if stage_id == "household-details":
                existing_household_members = FostererPersonInHomeDetail.objects.filter(
                    fosterer_profile=fosterer_profile
                ).order_by("id")

                for index, detail_form in enumerate(person_in_home_detail_formset):
                    if detail_form.is_valid() and detail_form.has_changed():
                        detail_data = detail_form.cleaned_data
                        if index < len(existing_household_members):
                            existing_detail = existing_household_members[index]
                            existing_detail.name = detail_data.get("name")
                            existing_detail.relation = detail_data.get("relation")
                            existing_detail.age = detail_data.get("age")
                            existing_detail.email = detail_data.get("email")
                            existing_detail.save()
                        else:
                            FostererPersonInHomeDetail.objects.create(
                                fosterer_profile=fosterer_profile,
                                name=detail_data.get("name"),
                                relation=detail_data.get("relation"),
                                age=detail_data.get("age"),
                                email=detail_data.get("email"),
                            )

            is_previous = "submit_prev" in request.POST
            after = request.GET.get('after', '')

            if is_previous:
                return redirect(f"/fosterer/{prev_stage}?after={after}")
            else:
                return redirect(f"/fosterer/{next_stage}?after={after}")

    else:
        form = form_class(instance=fosterer_profile)

        existing_pets = FostererExistingPetDetail.objects.filter(
            fosterer_profile=fosterer_profile
        ).order_by("id")

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

        persons_in_home = FostererPersonInHomeDetail.objects.filter(
            fosterer_profile=fosterer_profile
        )
        num_people = persons_in_home.count()
        extra_forms_needed = max(0, 6 - num_people)
        PersonInHomeDetailFormSet = formset_factory(
            PersonInHomeDetailForm, extra=extra_forms_needed
        )
        person_data = [model_to_dict(person) for person in persons_in_home]
        person_in_home_detail_formset = PersonInHomeDetailFormSet(
            prefix="personinhomedetail", initial=person_data
        )

    return render(
        request,
        "fosterer_profile/edit.html",
        {
            "user": user,
            "form": form,
            "existing_pet_detail_formset": existing_pet_detail_formset,
            "reference_detail_formset": reference_detail_formset,
            "person_in_home_detail_formset": person_in_home_detail_formset,
            "pageTitle": "Edit your fosterer profile",
            "stageNumber": stage_number,
            "stage_id": stage_id,
        },
    )
