from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest, PermissionDenied
from django.core.paginator import Paginator
from django.forms import DateInput, ModelForm
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from caim_base.views.awg.user_permissions import (
    check_awg_user_permissions_update_context,
)

from ...animal_petfinder_import import ImportAnimalError, import_animal_from_petfinder
from ...animal_search import query_animals
from ...models.animals import Animal, AnimalImage
from ...models.awg import Awg


@login_required()
@require_http_methods(["GET"])
def list_animals(request, awg_id):
    awg = get_object_or_404(Awg, pk=awg_id)

    # @todo pagination
    current_page = 1
    npp = 100

    query = query_animals(
        request.user,
        awg_id=awg.id,
        hide_unpublished_animals=False,
        hide_unpublished_awgs=False,
    )
    all_animals = query.all()
    paginator = Paginator(all_animals, npp)
    animals = paginator.page(current_page)

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name} | Manage animals",
        "animals": animals,
        "paginator": paginator,
    }
    context = check_awg_user_permissions_update_context(
        request, awg, ["MANAGE_ANIMALS"], context
    )
    return render(request, "awg/manage/animals/list.html", context)


@login_required()
@require_http_methods(["POST"])
def publish_animal(request, awg_id, animal_id):
    awg = get_object_or_404(Awg, pk=awg_id)

    try:
        animal = Animal.objects.get(id=animal_id, awg_id=awg_id)
    except Animal.DoesNotExist:
        raise Http404("Animal not found")

    if request.POST["action"] == "PUBLISH":
        if not animal.can_be_published():
            messages.error(request, "Animal cannot be published")
        else:
            animal.is_published = True
            animal.save()
            messages.success(request, "Animal was published")
    elif request.POST["action"] == "UNPUBLISH":
        animal.is_published = False
        animal.save()
        messages.success(request, "Animal was unpublished")
    else:
        raise BadRequest("Unknown action")

    return redirect(f"{awg.get_absolute_url()}/animals/{animal.id}")


class NativeDateInput(DateInput):
    input_type = "date"


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
                "awg_internal_id",
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
                "Behavior",
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
            "awg_internal_id",
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
        widgets = {
            "euth_date": NativeDateInput(),
        }
        labels = {"awg_internal_id": "Your ID for this animal"}


@login_required()
@require_http_methods(["POST", "GET"])
def edit_animal(request, awg_id, animal_id):
    awg = get_object_or_404(Awg, pk=awg_id)

    try:
        animal = Animal.objects.get(id=animal_id, awg_id=awg_id)
    except Animal.DoesNotExist:
        raise Http404("Animal not found")

    if request.POST:
        form = AwgAnimalForm(request.POST, instance=animal)
        if form.is_valid():
            animal = form.save()
            messages.success(request, "Animal was updated")
            return redirect(f"{awg.get_absolute_url()}/animals/{animal.id}")
        else:
            messages.error(request, "Please correct form errors")
    else:
        form = AwgAnimalForm(instance=animal)

    photos = animal.animalimage_set.all()

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name} | Edit animal",
        "form": form,
        "animal": animal,
        "photos": photos,
    }
    context = check_awg_user_permissions_update_context(
        request, awg, ["MANAGE_ANIMALS"], context
    )
    return render(request, "awg/manage/animals/edit.html", context)


def add_animal(request, awg_id):
    awg = get_object_or_404(Awg, pk=awg_id)

    if request.POST:
        form = AwgAnimalForm(request.POST, submit_label="Add animal")
        if form.is_valid():
            animal = form.save(commit=False)
            animal.awg = awg
            animal.save()
            messages.success(request, "Animal was added")
            return redirect(f"{awg.get_absolute_url()}/animals/{animal.id}")
        else:
            messages.error(request, "Please correct form errors")
    else:
        form = AwgAnimalForm(submit_label="Add animal")

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name} | Edit animal",
        "form": form,
    }
    context = check_awg_user_permissions_update_context(
        request, awg, ["MANAGE_ANIMALS"], context
    )
    return render(request, "awg/manage/animals/add.html", context)


@login_required()
@require_http_methods(["POST"])
def animal_photos(request, awg_id, animal_id):
    awg = get_object_or_404(Awg, pk=awg_id)

    try:
        animal = Animal.objects.get(id=animal_id, awg_id=awg_id)
    except Animal.DoesNotExist:
        raise Http404("Animal not found")

    action = request.POST["action"]

    try:
        if action == "ADD_PHOTO":
            if "photo" in request.FILES:
                file = request.FILES["photo"]
                file_name = f"${animal.id}_${file.name}"
                if not file.content_type in ("image/jpeg", "image/gif", "image/png"):
                    raise BadRequest(
                        "Cannot upload this file type. Please make sure its a jpeg, png or gif image."
                    )
                if animal.primary_photo:
                    new_animalimage = AnimalImage(
                        animal=animal, photo=animal.primary_photo
                    )
                    new_animalimage.photo.save(file_name, file)
                    new_animalimage.save()
                else:
                    animal.primary_photo.save(file_name, file)
                    animal.save()
                messages.success(request, "Animal photo was added")
        else:
            animalimage_id = request.POST["animalimage_id"]
            if not action or not animalimage_id:
                raise BadRequest("Missing parameters")

            animalimage = AnimalImage.objects.get(id=animalimage_id)

            if action == "DELETE":
                animalimage.delete()
                messages.success(request, "Animal photo was deleted")
            elif action == "MAKE_PRIMARY":
                if animal.primary_photo:
                    new_animalimage = AnimalImage(
                        animal=animal, photo=animal.primary_photo
                    )
                    new_animalimage.save()
                animal.primary_photo = animalimage.photo
                animal.save()
                animalimage.delete()
                messages.success(request, "Animal primary photo updated")
            else:
                raise BadRequest("Unknown action")
    except BadRequest as e:
        messages.error(request, str(e))

    return redirect(f"{awg.get_absolute_url()}/animals/{animal.id}")


class ImportURLForm(forms.Form):
    url = forms.URLField(label="URL")
    helper = FormHelper()
    helper.add_input(Submit("submit", "Submit", css_class="btn-primary"))
    helper.form_method = "POST"


@login_required()
@require_http_methods(["GET", "POST"])
def import_animal(request, awg_id):
    awg = get_object_or_404(Awg, pk=awg_id)

    if request.POST:
        form = ImportURLForm(request.POST)
        if form.is_valid():
            try:
                url = request.POST["url"].strip()
                animal = import_animal_from_petfinder(awg, url)
                messages.success(request, "Animal imported")
                if animal.primary_breed.name == "Unknown":
                    messages.warning(
                        request,
                        "Primary Animal breed is unknown, please update it below.",
                    )
                return redirect(f"{awg.get_absolute_url()}/animals/{animal.id}")
            except ImportAnimalError as e:
                messages.error(request, str(e))
    else:
        form = ImportURLForm()

    context = {"awg": awg, "pageTitle": f"Import from petfinder", "form": form}
    return render(request, "awg/manage/animals/import.html", context)
