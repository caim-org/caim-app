import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.gis.db.models import PointField
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from phonenumber_field.modelfields import PhoneNumberField
from .templatetags.caim_helpers import image_resize
from .states import states

logger = logging.getLogger(__name__)


User = get_user_model()
# Change default User model so email is unique and main identifier
User._meta.get_field("email")._unique = True
User.USERNAME_FIELD = "email"
User.REQUIRED_FIELDS = ["username"]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)


class ZipCode(models.Model):
    zip_code = models.CharField(max_length=16, unique=True)
    geo_location = PointField()


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
        verbose_name="Organisation type",
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
    email = models.EmailField(max_length=32, blank=True, null=True, default=None)
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

    def get_permissions_for_user(self, user):
        ret = []
        # If CAIM staff, all permissions
        if user.is_staff:
            ret.append("EDIT_PROFILE")
            ret.append("MANAGE_ANIMALS")
            ret.append("MANAGE_MEMBERS")
        # Look for AWGMember for this user and AWG
        member = self.awgmember_set.filter(user=user).first()
        if member:
            if member.canEditProfile:
                ret.append("EDIT_PROFILE")
            if member.canManageAnimals:
                ret.append("MANAGE_ANIMALS")
            if member.canManageMembers:
                ret.append("MANAGE_MEMBERS")
        return ret

    def get_absolute_url(self):
        return f"/organization/{self.id}"

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "user",
            "awg",
        )


class AnimalType(models.TextChoices):
    DOG = "DOG", "Dog"
    CAT = "CAT", "Cat"


class Breed(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    animal_type = models.CharField(
        max_length=3,
        choices=AnimalType.choices,
        default=AnimalType.DOG,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.animal_type})"


class Animal(models.Model):
    class AnimalSex(models.TextChoices):
        F = "F", "Female"
        M = "M", "Male"

    class AnimalSize(models.TextChoices):
        XS = "XS", "X-Small"
        S = "S", "Small"
        M = "M", "Medium"
        L = "L", "Large"
        XL = "XL", "X-Large"

    class AnimalAge(models.TextChoices):
        BABY = "BABY", "Puppy/Kitten"
        YOUNG = "YOUNG", "Young"
        ADULT = "ADULT", "Adult"
        SENIOR = "SENIOR", "Senior"

    class AnimalBehaviourGrade(models.TextChoices):
        POOR = "POOR", "Poor"
        SELECTIVE = "SELECTIVE", "Selective"
        GOOD = "GOOD", "Good"
        NOT_TESTED = "NOT_TESTED", "Not tested"

    id = models.AutoField(primary_key=True, verbose_name="CAIM ID")
    name = models.CharField(max_length=100)
    animal_type = models.CharField(
        max_length=3,
        choices=AnimalType.choices,
        default=AnimalType.DOG,
    )
    petfinder_id = models.CharField(
        max_length=32, blank=True, null=True, default=None, unique=True
    )
    awg = models.ForeignKey(Awg, on_delete=models.CASCADE, verbose_name="AWG")
    awg_internal_id = models.CharField(
        max_length=64,
        null=True,
        default=None,
        blank=True,
        verbose_name="AWG internal ID",
    )
    awg_profile_url = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
        verbose_name="AWG animal profile URL",
    )
    is_published = models.BooleanField(default=True)
    primary_breed = models.ForeignKey(
        Breed, on_delete=models.RESTRICT, related_name="primary_animal_set"
    )
    secondary_breed = models.ForeignKey(
        Breed,
        on_delete=models.RESTRICT,
        related_name="secondary_animal_set",
        blank=True,
        null=True,
        default=None,
    )
    is_mixed_breed = models.BooleanField()
    is_unknown_breed = models.BooleanField()
    sex = models.CharField(
        max_length=1,
        choices=AnimalSex.choices,
    )
    size = models.CharField(
        max_length=2,
        choices=AnimalSize.choices,
    )
    age = models.CharField(
        max_length=8,
        choices=AnimalAge.choices,
    )
    is_spayed_neutered = models.BooleanField(verbose_name="Is spayed / neutered")
    is_vaccinations_current = models.BooleanField(
        verbose_name="Vaccinations are up to date"
    )
    is_special_needs = models.BooleanField(verbose_name="Has special needs")
    special_needs = models.TextField(blank=True, verbose_name="Special needs details")
    vaccinations_notes = models.TextField(blank=True, verbose_name="Vaccination notes")
    description = models.TextField(blank=True)
    behaviour_dogs = models.CharField(
        max_length=10,
        choices=AnimalBehaviourGrade.choices,
        default=AnimalBehaviourGrade.NOT_TESTED,
        verbose_name="Behavour with dogs",
    )
    behaviour_cats = models.CharField(
        max_length=10,
        choices=AnimalBehaviourGrade.choices,
        default=AnimalBehaviourGrade.NOT_TESTED,
        verbose_name="Behavour with cats",
    )
    behaviour_kids = models.CharField(
        max_length=10,
        choices=AnimalBehaviourGrade.choices,
        default=AnimalBehaviourGrade.NOT_TESTED,
        verbose_name="Behavour with kidw",
    )
    is_euth_listed = models.BooleanField(verbose_name="Is scheduled for euthanasia")
    euth_date = models.DateField(
        blank=True, null=True, default=None, verbose_name="Scheduled euthanasia date"
    )
    primary_photo = models.ImageField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def breedsText(self):
        if self.is_unknown_breed:
            return "Unknown breed"
        text = self.primary_breed.name
        if self.secondary_breed and self.secondary_breed != self.primary_breed:
            text = f"{self.primary_breed.name} / {self.secondary_breed.name}"
        if self.is_mixed_breed:
            text = f"{text} mix"
        return text

    def sexText(self):
        return Animal.AnimalSex[self.sex].label

    def ageText(self):
        return Animal.AnimalAge[self.age].label

    def sizeText(self):
        return Animal.AnimalSize[self.size].label

    def get_absolute_url(self):
        return f"/animal/{self.id}"

    def admin_image_tag(self):
        if self.primary_photo:
            resized_url = image_resize(self.primary_photo.url, "45x45")
            return mark_safe(
                '<img src="%s" style="max-width: 45px; max-height:45px;" />'
                % resized_url
            )
        else:
            return "No Photo"

    admin_image_tag.short_description = "Image"


class AnimalImage(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    photo = models.ImageField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)


class AnimalShortList(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("animal", "user"),)


class AnimalComment(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(blank=True, null=True)

    def can_be_deleted_by(self, user):
        return self.can_be_edited_by(user)

    def can_be_edited_by(self, user):
        return self.user == user or user.is_staff
