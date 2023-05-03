from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from .models.awg import User


class NewUserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(widget=forms.TextInput(attrs={"autofocus": ""}))
    last_name = forms.CharField()
    zip_code = forms.CharField(
        validators=[
            RegexValidator(
                regex=r"^\b\d{5}(-\d{4})?\b$", message="Please enter a valid ZIP code."
            )
        ]
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
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
            "username": "Your name as you want it to appear on the site. "
            + "This will be visible publicly.",
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
