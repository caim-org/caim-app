import logging
import urllib
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.gis.db.models import PointField
from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from ..states import states
from ..utils import full_url
from .geo import ZipCode
from .user import User

logger = logging.getLogger(__name__)


class Awg(models.Model):
    class AwgType(models.TextChoices):
        SHELTER_ONLY = "SHELTER_ONLY", "Shelter only"
        FOSTER_ONLY = "FOSTER_ONLY", "Foster only"
        SHELTER_AND_FOSTER = "SHELTER_AND_FOSTER", "Both Shelter and Foster"

    class AwgStatus(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        PUBLISHED = "PUBLISHED", "Published"
        UNPUBLISHED = "UNPUBLISHED", "Unpublished"

    id = models.AutoField(primary_key=True, verbose_name="CAIM ID")
    name = models.CharField(max_length=100, verbose_name="Organization name")
    petfinder_id = models.CharField(max_length=32, blank=True, null=True, default=None)
    status = models.CharField(
        max_length=16,
        choices=AwgStatus.choices,
        default=AwgStatus.APPLIED,
        verbose_name="Listing status",
    )
    description = models.TextField(blank=True)
    awg_type = models.CharField(
        max_length=32,
        choices=AwgType.choices,
        default=None,
        blank=True,
        null=True,
        verbose_name="Organization type",
    )

    has_501c3_tax_exemption = models.BooleanField(
        default=False, verbose_name="501c3 tax exempt charity"
    )
    company_ein = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        default=None,
        verbose_name="Employer Identification Number (EIN)",
    )

    workwith_dogs = models.BooleanField(default=False, verbose_name="Works with dogs?")
    workwith_cats = models.BooleanField(default=False, verbose_name="Works with cats?")
    workwith_other = models.BooleanField(
        default=False, verbose_name="Works with other animals?"
    )

    geo_location = PointField()
    zip_code = models.CharField(max_length=16, blank=True, null=True, default=None)
    city = models.CharField(max_length=32, blank=True, null=True, default=None)
    state = models.CharField(max_length=2, choices=states.items())
    is_exact_location_shown = models.BooleanField(
        default=False, verbose_name="Show exact location?"
    )
    email = models.EmailField(max_length=255, blank=True, null=True, default=None)
    phone = PhoneNumberField(blank=True, null=True, default=None)
    website_url = models.URLField(
        max_length=255, blank=True, null=True, default=None, verbose_name="Website URL"
    )
    facebook_url = models.URLField(
        max_length=255, blank=True, null=True, default=None, verbose_name="Facebook URL"
    )
    instagram_url = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
        verbose_name="Instagram URL",
    )
    twitter_url = models.URLField(
        max_length=255, blank=True, null=True, default=None, verbose_name="Twitter URL"
    )
    tiktok_url = models.URLField(
        max_length=255, blank=True, null=True, default=None, verbose_name="TikTok URL"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def user_is_member_of_awg(self, user):
        if not user.id:
            return False
        member = self.awgmember_set.filter(user=user).first()
        return bool(member)

    def get_permissions_for_user(self, user):
        ret = []
        if not user.id:
            return ret
        # If CAIM staff, all permissions
        if user.is_staff:
            ret.append("EDIT_PROFILE")
            ret.append("MANAGE_ANIMALS")
            ret.append("MANAGE_MEMBERS")
            ret.append("MANAGE_APPLICATIONS")
        # Look for AWGMember for this user and AWG
        member = self.awgmember_set.filter(user=user).first()
        if member:
            if member.canEditProfile:
                ret.append("EDIT_PROFILE")
            if member.canManageAnimals:
                ret.append("MANAGE_ANIMALS")
            if member.canManageMembers:
                ret.append("MANAGE_MEMBERS")
            if member.canManageApplications:
                ret.append("MANAGE_APPLICATIONS")
            if member.canViewApplications:
                ret.append("VIEW_APPLICATIONS")
        return ret

    def get_absolute_url(self):
        return full_url(f"/organization/{self.id}")

    def is_currently_published(self):
        return self.status == Awg.AwgStatus.PUBLISHED

    def clean(self):
        # Validate zip_code
        if self.zip_code:
            zip_info = ZipCode.objects.filter(zip_code=self.zip_code).first()
            if not zip_info:
                raise ValidationError({"zip_code": "Invalid US zip code"})

    def save(self, *args, **kwargs):
        try:
            zip_info = ZipCode.objects.get(zip_code=self.zip_code)
            self.geo_location = zip_info.geo_location
        except:
            logger.warn("ZIP code not valid")
        super(Awg, self).save(*args, **kwargs)


class AwgMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    awg = models.ForeignKey(Awg, on_delete=models.CASCADE)
    canEditProfile = models.BooleanField(default=False)
    canManageAnimals = models.BooleanField(default=False)
    canManageMembers = models.BooleanField(default=False)
    canManageApplications = models.BooleanField(default=False)
    canViewApplications = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "user",
            "awg",
        )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_email": self.user.email,
            "user_username": self.user.username,
            "awg_id": self.awg_id,
            "canEditProfile": self.canEditProfile,
            "canManageAnimals": self.canManageAnimals,
            "canManageMembers": self.canManageMembers,
            "canManageApplications": self.canManageApplications,
            "canViewApplications": self.canViewApplications,
        }
