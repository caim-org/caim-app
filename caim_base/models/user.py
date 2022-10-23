from django.db import models
from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()
# Change default User model so email is unique and main identifier
User._meta.get_field("email")._unique = True
User.USERNAME_FIELD = "email"
User.REQUIRED_FIELDS = ["username"]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
