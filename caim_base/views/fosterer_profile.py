
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.contrib import messages

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit

from ..models.fosterer import FostererProfile

STAGES = [
    "about-you",
    "animal-preferences",
    "pet-experience",
    "references",
    "household-details",
    "final-thoughts",
    "submit"
]

class FostererProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        stage = STAGES[0]
        submit_label = "Submit application" if stage=='submit' else "Next stage"

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
            Fieldset(
                "Animal preferences",
                "type_of_animals",
                "category_of_animals",
                "behavioural_attributes",
                "timeframe",
                "timeframe_other"
            ),
            Fieldset(
                "Pet Experience",
                "num_existing_pets",
                "existing_pets_details",
                "experience_description",
                "experience_categories",
                "experience_given_up_pet",
            ),
            Fieldset(
                "References",
                "reference_1",
                "reference_2",
                "reference_3",
            ),
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
            Fieldset(
                "Final thoughts",
                "other_info",
                "ever_been_convicted_abuse",
                "agree_share_details",
            ),
            Submit("submit", submit_label, css_class="button"),
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
            
            "type_of_animals",
            "category_of_animals",
            "behavioural_attributes",
            "timeframe",
            "timeframe_other",

            "num_existing_pets",
            "existing_pets_details",
            "experience_description",
            "experience_categories",
            "experience_given_up_pet",

            "reference_1",
            "reference_2",
            "reference_3",

            "people_at_home",
            "yard_type",
            "yard_fence_over_5ft",
            "rent_own",
            "rent_restrictions",
            "rent_ok_foster_pets",
            "hours_alone_description",
            "hours_alone_location",
            "sleep_location",

            "other_info",
            "ever_been_convicted_abuse",
            "agree_share_details",
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
            
            "type_of_animals",
            "category_of_animals",
            "timeframe",

            "num_existing_pets",
            "existing_pets_details",
            "experience_description",
            "experience_categories",
            
            "reference_1",
            "reference_2",
            "reference_3",

            "people_at_home",
            "yard_type",
            "rent_own",
            "hours_alone_description",
            "hours_alone_location",
            "sleep_location",

            "ever_been_convicted_abuse",
            "agree_share_details",
        )


@login_required()
@require_http_methods(["POST", "GET"])
def edit(request):
    user = request.user
    
    try:
        fosterer_profile = FostererProfile.objects.get(user=user)
    except FostererProfile.DoesNotExist:
        # Create a blank profile for this user
        fosterer_profile = FostererProfile(user=user)
        fosterer_profile.email = user.email
        fosterer_profile.save()
    
    if request.method == "POST":
        form = FostererProfileForm(request.POST, instance=fosterer_profile)
        if form.is_valid():
            fosterer_profile = form.save()
            messages.success(request, "Profile was updated")
            #return redirect(f"{awg.get_absolute_url()}/animals/{animal.id}")
        else:
            messages.error(request, "Please correct form errors")
    else:
        form = FostererProfileForm(instance=fosterer_profile)

    return render(
        request,
        "fosterer_profile/edit.html",
        {"user": user, "form": form, "pageTitle": "Edit your fosterer profile"},
    )
