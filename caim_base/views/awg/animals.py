from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied, BadRequest
from django.http import Http404
from django.core.paginator import Paginator
from django.forms import ModelForm, DateInput
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit

from ...models import Awg, Animal, AnimalImage
from ...animal_search import query_animals


def check_awg_user_permissions(request, awg_id):
    try:
        awg = Awg.objects.get(id=awg_id)
    except Awg.DoesNotExist:
        raise Http404("Awg not found")

    current_user_permissions = awg.get_permissions_for_user(request.user)
    if not "MANAGE_ANIMALS" in current_user_permissions:
        raise PermissionDenied(
            "User does not have permission to manage animals for this AWG"
        )
    return awg, current_user_permissions


@login_required()
@require_http_methods(["GET"])
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
        widgets = {
            "euth_date": NativeDateInput(),
        }


@login_required()
@require_http_methods(["POST", "GET"])
def edit_animal(request, awg_id, animal_id):
    awg, current_user_permissions = check_awg_user_permissions(request, awg_id)

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
        "currentUserPermissions": current_user_permissions,
        "form": form,
        "animal": animal,
        "photos": photos,
    }
    return render(request, "awg/manage/animals/edit.html", context)


def add_animal(request, awg_id):
    awg, current_user_permissions = check_awg_user_permissions(request, awg_id)

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
        "currentUserPermissions": current_user_permissions,
        "form": form,
    }
    return render(request, "awg/manage/animals/add.html", context)


@login_required()
@require_http_methods(["POST"])
def animal_photos(request, awg_id, animal_id):
    awg, current_user_permissions = check_awg_user_permissions(request, awg_id)

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
