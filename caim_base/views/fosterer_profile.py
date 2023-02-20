from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, RadioSelect
from django.contrib import messages
from django.http import Http404

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit

from ..models.fosterer import FostererProfile
from ..notifications import notify_new_fosterer_profile

class FostererProfileStage1Form(ModelForm):
    def __init__(self, *args, **kwargs):
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
                "email",
                "phone",
                "street_address",
                "city",
                "state",
                "zip_code",
            ),
            Submit("submit", "Next page", css_class="button"),
        )

    class Meta:
        model = FostererProfile
        fields = [
            "firstname",
            "lastname",
            "email",
            "phone",
            "street_address",
            "city",
            "state",
            "zip_code",
        ]
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
                "behavioural_attributes",
                "timeframe",
                "timeframe_other"
            ),
            Submit("submit_prev", "&laquo; Previous page", css_class="btn btn-secondary"),
            Submit("submit", "Next page &raquo;", css_class="btn btn-primary"),
        )

    class Meta:
        model = FostererProfile
        fields = [
            "type_of_animals",
            "category_of_animals",
            "behavioural_attributes",
            "timeframe",
            "timeframe_other",
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

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Pet Experience",
                "num_existing_pets",
                "existing_pets_details",
                "experience_description",
                "experience_categories",
                "experience_given_up_pet",
            ),
            Submit("submit_prev", "&laquo; Previous page", css_class="btn btn-secondary"),
            Submit("submit", "Next page &raquo;", css_class="btn btn-primary"),
        )

    class Meta:
        model = FostererProfile
        fields = [
            "num_existing_pets",
            "existing_pets_details",
            "experience_description",
            "experience_categories",
            "experience_given_up_pet",
        ]
        required = (
            "num_existing_pets",
            "existing_pets_details",
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
                "reference_1",
                "reference_2",
                "reference_3",
            ),
            Submit("submit_prev", "&laquo; Previous page", css_class="btn btn-secondary"),
            Submit("submit", "Next page &raquo;", css_class="btn btn-primary"),
        )

    class Meta:
        model = FostererProfile
        fields = [
            "reference_1",
            "reference_2",
            "reference_3",
        ]
        required = (
            "reference_1",
            "reference_2",
            "reference_3",
        )

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
                "people_at_home",
                "yard_type",
                "yard_fence_over_5ft",
                "rent_own",
                "rent_restrictions",
                "rent_ok_foster_pets",
                "hours_alone_description",
                "hours_alone_location",
                "sleep_location"
            ),
            Submit("submit_prev", "&laquo; Previous page", css_class="btn btn-secondary"),
            Submit("submit", "Next page &raquo;", css_class="btn btn-primary"),
        )

    class Meta:
        model = FostererProfile
        fields = [
            "people_at_home",
            "yard_type",
            "yard_fence_over_5ft",
            "rent_own",
            "rent_restrictions",
            "rent_ok_foster_pets",
            "hours_alone_description",
            "hours_alone_location",
            "sleep_location",
        ]
        required = (
            "people_at_home",
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
            "rent_ok_foster_pets": RadioSelect(),
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
            ),
            Submit("submit_prev", "&laquo; Previous page", css_class="btn btn-secondary"),
            Submit("submit", "Next page &raquo;", css_class="btn btn-primary"),
        )
    class Meta:
        model = FostererProfile
        fields = [
            "other_info",
            "ever_been_convicted_abuse",
            "agree_share_details",
        ]
        required = (
            "ever_been_convicted_abuse",
            "agree_share_details",
        )
        widgets = {
            "ever_been_convicted_abuse": RadioSelect(),
            "agree_share_details": RadioSelect(),
        }

STAGES = {
    "about-you": {
        "number":1,
        "form_class": FostererProfileStage1Form,
        "next": "animal-preferences",
        "prev": None,
    },
    "animal-preferences": {
        "number":2,
        "form_class": FostererProfileStage2Form,
        "next": "pet-experience",
        "prev": "about-you",
    },
    "pet-experience": {
        "number":3,
        "form_class": FostererProfileStage3Form,
        "next": "references",
        "prev": "animal-preferences",
    },
    "references": {
        "number":4,
        "form_class": FostererProfileStage4Form,
        "next": "household-details",
        "prev": "pet-experience",
    },
    "household-details": {
        "number":5,
        "form_class": FostererProfileStage5Form,
        "next": "final-thoughts",
        "prev": "references",
    },
    "final-thoughts": {
        "number":6,
        "form_class": FostererProfileStage6Form,
        "next": "complete",
        "prev": "household-details",
    }
}

@login_required()
@require_http_methods(["GET"])
def start(request):
    return redirect('/fosterer/about-you')

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

    if stage_id=='complete':
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
                "pageTitle": "Foster application complete",
            },
        )

    if not stage_id in STAGES:
        raise Http404("Stage not found")

    stage = STAGES[stage_id]
    stage_number = stage['number']
    form_class = stage['form_class']
    next_stage = stage['next']
    prev_stage = stage['prev']

    if request.method == "POST":
        form = form_class(request.POST, instance=fosterer_profile)
        if form.is_valid():
            fosterer_profile = form.save()
            is_previous = 'submit_prev' in request.POST
            if is_previous:
                return redirect(f"/fosterer/{prev_stage}")
            else:
                return redirect(f"/fosterer/{next_stage}")
        else:
            messages.error(request, "Please correct form errors")
    else:
        form = form_class(instance=fosterer_profile)

    return render(
        request,
        "fosterer_profile/edit.html",
        {
            "user": user, 
            "form": form, 
            "pageTitle": "Edit your fosterer profile",
            "stageNumber": stage_number,
        },
    )
