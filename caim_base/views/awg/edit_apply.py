from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from ...models.awg import Awg, AwgMember
from ...notifications import notify_new_awg_application


class AwgForm(ModelForm):
    website_url = forms.URLField(
        label="Website URL",
        required=True,
        widget=forms.TextInput(attrs={"type": "text"}),
    )
    facebook_url = forms.URLField(
        label="Facebook URL",
        required=False,
        widget=forms.TextInput(attrs={"type": "text"}),
    )
    instagram_url = forms.URLField(
        label="Instagram URL",
        required=False,
        widget=forms.TextInput(attrs={"type": "text"}),
    )
    twitter_url = forms.URLField(
        label="Twitter URL",
        required=False,
        widget=forms.TextInput(attrs={"type": "text"}),
    )
    tiktok_url = forms.URLField(
        label="TikTok URL",
        required=False,
        widget=forms.TextInput(attrs={"type": "text"}),
    )

    def __init__(self, *args, **kwargs):
        submit_label = kwargs.pop("submit_label", "Update organization profile")
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "About your organization",
                "name",
                "description",
                "has_501c3_tax_exemption",
                "email",
                "phone",
                "company_ein",
            ),
            Fieldset(
                "How you help animals",
                "awg_type",
                "workwith_dogs",
                "workwith_cats",
                "workwith_other",
            ),
            Fieldset(
                "Address information",
                "state",
                "city",
                "zip_code",
                "is_exact_location_shown",
            ),
            Fieldset(
                "Websites and Social media",
                "website_url",
                "facebook_url",
                "instagram_url",
                "twitter_url",
                "tiktok_url",
            ),
            Submit("submit", submit_label, css_class="button white"),
        )

    class Meta:
        model = Awg
        fields = [
            "name",
            "description",
            "awg_type",
            "has_501c3_tax_exemption",
            "company_ein",
            "workwith_dogs",
            "workwith_cats",
            "workwith_other",
            "zip_code",
            "city",
            "state",
            "is_exact_location_shown",
            "email",
            "phone",
            "website_url",
            "facebook_url",
            "instagram_url",
            "twitter_url",
            "tiktok_url",
        ]
        required = (
            "name",
            "description",
            "awg_type",
            "company_ein",
            "city",
            "state",
            "zip_code",
            "email",
            "website_url",
        )
        labels = {
            "workwith_dogs": "We work with Dogs",
            "workwith_cats": "We work with Cats",
            "workwith_other": "We work with other animals",
            "is_exact_location_shown": (
                "Should we show your exact location (zip and map) publicly?"
            ),
            "has_501c3_tax_exemption": "We are a 501c3 tax exempt charity",
            "email": "Contact email address",
            "phone": "Contact phone number",
        }


@login_required()
@require_http_methods(["POST", "GET"])
def edit(request, awg_id):
    try:
        awg = Awg.objects.get(id=awg_id)
    except Awg.DoesNotExist as e:
        raise Http404("Awg not found") from e

    current_user_permissions = awg.get_permissions_for_user(request.user)
    if "EDIT_PROFILE" not in current_user_permissions:
        raise PermissionDenied("User does not have permission to edit this AWG")

    if request.POST:
        form = AwgForm(request.POST, instance=awg)
        if form.is_valid():
            form.save()
    else:
        form = AwgForm(instance=awg)

    current_user_permissions = awg.get_permissions_for_user(request.user)

    context = {
        "awg": awg,
        "pageTitle": f"{awg.name} | Edit profile",
        "form": form,
        "currentUserPermissions": current_user_permissions,
    }
    return render(request, "awg/manage/edit-profile.html", context)


@require_http_methods(["POST", "GET"])
def create(request):
    if not request.user.is_authenticated:
        return render(
            request,
            "awg/apply/must-login.html",
            {"pageTitle": "Create organization profile"},
        )

    if request.POST:
        form = AwgForm(request.POST, submit_label="Submit form")
        if form.is_valid():
            awg = form.save(commit=False)
            awg.status = Awg.AwgStatus.APPLIED
            awg.save()
            member = AwgMember(
                user=request.user,
                awg=awg,
                canEditProfile=True,
                canManageAnimals=True,
                canManageMembers=True,
            )
            member.save()  # Add current user as full admin member

            try:
                notify_new_awg_application(awg)
            except Exception:
                print("Could not send email")

            return render(request, "awg/apply/success.html", {"pageTitle": "Success"})
    else:
        form = AwgForm(submit_label="Submit form")

    context = {"pageTitle": "Create organization profile", "form": form}
    return render(request, "awg/apply/form.html", context)
