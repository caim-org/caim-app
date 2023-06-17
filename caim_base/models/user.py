from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..states import states

User = get_user_model()
# Change default User model so email is unique and main identifier
User._meta.get_field("email")._unique = True
User.USERNAME_FIELD = "email"
User.REQUIRED_FIELDS = ["username"]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    city = models.CharField(_("city"), max_length=32, blank=True)
    state = models.CharField(
        _("state"),
        max_length=2,
        blank=True,
        null=True,
        choices=states.items(),
        default=None,
    )
    zip_code = models.CharField(_("ZIP code"), max_length=10, blank=True)
    salesforce_id = models.CharField(max_length=32, null=True)
