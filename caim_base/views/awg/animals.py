from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.core.paginator import Paginator
from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit

from ...models import Awg, Animal
from ...animal_search import query_animals


def check_awg_user_permissions(request, awg_id):
    try:
        awg = Awg.objects.get(id=awg_id)
    except Awg.DoesNotExist:
        raise Http404("Awg not found")

    current_user_permissions = awg.get_permissions_for_user(request.user)
    if not "MANAGE_ANIMALS" in current_user_permissions:
        raise PermissionDenied(
            "User does not have permission to manage members for this AWG"
        )
    return awg, current_user_permissions


def list_animals(request, awg_id):
    awg, current_user_permissions = check_awg_user_permissions(request, awg_id)

    # @todo pagination
    current_page = 1
    npp = 100

    query = query_animals(request.user, awg_id=awg.id)
    all_animals = query.all()
    paginator = Paginator(all_animals, npp)
    animals = paginator.page(current_page)

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name} | Animals",
        "currentUserPermissions": current_user_permissions,
        "animals": animals,
        "paginator": paginator,
    }
    return render(request, "awg/manage/animals/list.html", context)


class AwgAnimalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        submit_label = kwargs.pop("submit_label", "Update animal")
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "About animal",
                "name",
                "animal_type",
                "primary_breed",
                "secondary_breed",
                "is_mixed_breed",
                "is_unknown_breed",
                "sex",
                "age",
                "size",
                "description",
            ),
            Fieldset(
                "Behavour",
                "behaviour_dogs",
                "behaviour_cats",
                "behaviour_kids",
            ),
            Fieldset(
                "Medical notes",
                "is_spayed_neutered",
                "is_vaccinations_current",
                "vaccinations_notes",
                "is_special_needs",
                "special_needs",
            ),
            Fieldset(
                "Red list",
                "is_euth_listed",
                "euth_date",
            ),
            Submit("submit", submit_label, css_class="button white"),
        )

    class Meta:
        model = Animal
        fields = [
            "name",
            "animal_type",
            "primary_breed",
            "secondary_breed",
            "is_mixed_breed",
            "is_unknown_breed",
            "sex",
            "age",
            "size",
            "description",
            "is_spayed_neutered",
            "is_vaccinations_current",
            "vaccinations_notes",
            "is_special_needs",
            "special_needs",
            "behaviour_dogs",
            "behaviour_cats",
            "behaviour_kids",
            "is_euth_listed",
            "euth_date",
        ]
        required = (
            "name",
            "animal_type",
            "sex",
        )
        labels = {
            "workwith_dogs": "We work with Dogs",
            "workwith_cats": "We work with Cats",
            "workwith_other": "We work with other animals",
            "is_exact_location_shown": "Should we show your exact location (zip and map) publically?",
            "has_501c3_tax_exemption": "We are a 501c3 tax exempt charity",
            "email": "Contact email address",
            "phone": "Contact phone number",
        }


def edit_animal(request, awg_id, animal_id):
    awg, current_user_permissions = check_awg_user_permissions(request, awg_id)

    try:
        animal = Animal.objects.get(id=animal_id, awg_id=awg_id)
    except Animal.DoesNotExist:
        raise Http404("Animal not found")

    form = AwgAnimalForm(instance=animal)

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name} | Edit animal",
        "currentUserPermissions": current_user_permissions,
        "form": form,
    }
    return render(request, "awg/manage/animals/edit.html", context)


def add_animal(request, awg_id):
    awg, current_user_permissions = check_awg_user_permissions(request, awg_id)

    form = AwgAnimalForm()

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name} | Edit animal",
        "currentUserPermissions": current_user_permissions,
        "form": form,
    }
    return render(request, "awg/manage/animals/add.html", context)
