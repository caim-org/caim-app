from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models.awg import User


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")
        labels = {
            "username": "Display name",
        }
        help_texts = {
            "username": "Your name as you want it to appear on the site. This will be visible publicly.",
            "email": "Your email address so we can contact you. This will not be visible publicly.",
        }

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        # Lowercase to avoid case sensitivity
        user.email = self.cleaned_data["email"].lower()
        if commit:
            user.save()
        return user
