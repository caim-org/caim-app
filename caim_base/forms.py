from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models.awg import User
from .models.geo import ZipCode
from .states import form_states


def zip_validator(zip_code: str):
    if not ZipCode.objects.filter(Q(zip_code=zip_code)).exists():
        raise ValidationError("Invalid US zip code")


class NewUserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(widget=forms.TextInput(attrs={"autofocus": ""}))
    last_name = forms.CharField()
    city = forms.CharField(max_length=32)
    state = forms.ChoiceField(choices=form_states.items())
    zip_code = forms.CharField(validators=[zip_validator])

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "city",
            "state",
            "zip_code",
            "username",
            "email",
            "password1",
            "password2",
        )
        labels = {
            "username": "Display name",
            "first_name": "First name",
            "last_name": "Last name",
            "zip_code": "ZIP code",
        }
        help_texts = {
            "username": "Your name as you want it to appear on the site."
            + "This will be visible publicly, and may not contain spaces.",
            "email": "Your email address so we can contact you. "
            + "This will not be visible publicly.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.pop(
            "autofocus", None  # Remove autofocus from email field
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        # Lowercase to avoid case sensitivity
        user.email = self.cleaned_data["email"].lower()
        if commit:
            user.save()
        return user
