import logging
from datetime import datetime, timedelta
import urllib

from django.utils import timezone
from django.db import models
from django.contrib.gis.db.models import PointField
from django.utils.safestring import mark_safe
from caim_base.templatetags.caim_helpers import image_resize
from ..utils import full_url
from .awg import Awg
from .user import User
from .geo import ZipCode

logger = logging.getLogger(__name__)


class AnimalType(models.TextChoices):
    DOG = "DOG", "Dog"
    CAT = "CAT", "Cat"

    @classmethod
    def pluralize(cls, animal_type: str) -> str:
        if animal_type.upper() == cls.DOG:
            return "Dogs"
        elif animal_type.upper() == cls.CAT:
            return "Cats"
        else:
            raise ValueError(f"unknown AnimalType {animal_type}")


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

    # @todo these ranges need to be animal type specific
    class AnimalSize(models.TextChoices):
        # XS = "XS", "X-Small"
        S = "S", "Small (0-25 lbs)"
        M = "M", "Medium (26-60 lbs)"
        L = "L", "Large (61-100 lbs)"
        XL = "XL", "X-Large (101 lbs+)"

    # @todo these ranges need to be animal type specific
    class AnimalAge(models.TextChoices):
        BABY = "BABY", "Baby (< 1 year)"
        YOUNG = "YOUNG", "Young (1-3 years)"
        ADULT = "ADULT", "Adult (3-8 years)"
        SENIOR = "SENIOR", "Senior (8+ years)"

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
    awg = models.ForeignKey(
        Awg, on_delete=models.CASCADE, verbose_name="AWG", related_name="animals"
    )
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
    is_published = models.BooleanField(default=False)
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
        verbose_name="Behavior with dogs",
    )
    behaviour_cats = models.CharField(
        max_length=10,
        choices=AnimalBehaviourGrade.choices,
        default=AnimalBehaviourGrade.NOT_TESTED,
        verbose_name="Behavior with cats",
    )
    behaviour_kids = models.CharField(
        max_length=10,
        choices=AnimalBehaviourGrade.choices,
        default=AnimalBehaviourGrade.NOT_TESTED,
        verbose_name="Behavior with kids",
    )
    is_euth_listed = models.BooleanField(verbose_name="Is scheduled for euthanasia")
    euth_date = models.DateField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Scheduled euthanasia date",
    )
    primary_photo = models.ImageField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_published_at = models.DateTimeField(blank=True, default=None, null=True)

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

    def get_absolute_url(self):
        return full_url(f"/animal/{self.id}")

    def can_be_published(self):
        return bool(self.primary_photo)

    def is_currently_published(self):
        # Is published and the owning awg published?
        return self.is_published and self.awg.is_currently_published()

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

    def save(self, *args, **kwargs):
        # Automatically unpublish is record no longer valid to be published
        if not self.can_be_published():
            self.is_published = False
        if not self.first_published_at and self.is_currently_published():
            self.first_published_at = datetime.now()
        super(Animal, self).save(*args, **kwargs)


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

    def get_sub_comments(self):
        return AnimalSubComment.objects.filter(comment=self.id)


class AnimalSubComment(models.Model):
    comment = models.ForeignKey(AnimalComment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(blank=True, null=True)

    def can_be_deleted_by(self, user):
        return self.can_be_edited_by(user)

    def can_be_edited_by(self, user):
        return self.user == user or user.is_staff

    def get_absolute_url(self):
        return full_url(f"/animal/{self.comment.animal.id}#comments")


class SavedSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=64,
    )
    animal_type = models.CharField(
        max_length=3,
        choices=AnimalType.choices,
        default=AnimalType.DOG,
    )
    zip_code = models.CharField(max_length=16, blank=True, null=True, default=None)
    geo_location = PointField()
    radius = models.IntegerField(blank=True, null=True, default=None)
    sex = models.CharField(
        max_length=1,
        choices=Animal.AnimalSex.choices,
        blank=True,
        null=True,
        default=None,
    )
    size = models.CharField(
        max_length=2,
        choices=Animal.AnimalSize.choices,
        blank=True,
        null=True,
        default=None,
    )
    age = models.CharField(
        max_length=8,
        choices=Animal.AnimalAge.choices,
        blank=True,
        null=True,
        default=None,
    )
    breed = models.ForeignKey(
        Breed,
        on_delete=models.CASCADE,
        related_name="+",  # Dont need related field on breed
        blank=True,
        null=True,
        default=None,
    )
    euth_date_within_days = models.IntegerField(blank=True, null=True, default=None)
    goodwith_cats = models.BooleanField(blank=True, null=True, default=None)
    goodwith_dogs = models.BooleanField(blank=True, null=True, default=None)
    goodwith_kids = models.BooleanField(blank=True, null=True, default=None)
    is_notifications_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_checked_at = models.DateTimeField(null=True, default=None, blank=True)
    check_every = models.DurationField(default=timedelta(days=1))

    def save(self, *args, **kwargs):
        try:
            zip_info = ZipCode.objects.get(zip_code=self.zip_code)
            self.geo_location = zip_info.geo_location
        except:
            logger.warn("ZIP code not valid")
        super(SavedSearch, self).save(*args, **kwargs)

    def get_absolute_url(self):
        query_params = {
            "zip": self.zip_code,
            "radius": self.radius,
            "sex": self.sex,
            "age": self.age,
            "size": self.size,
            "breed": self.breed.slug if self.breed else None,
            "euth_date": self.euth_date_within_days,
            "goodwith_cats": "on" if self.goodwith_cats else None,
            "goodwith_dogs": "on" if self.goodwith_dogs else None,
            "goodwith_kids": "on" if self.goodwith_kids else None,
        }
        # Remove None values
        filtered_query_params = {k: v for k, v in query_params.items() if v}
        query_string = urllib.parse.urlencode(filtered_query_params)
        return full_url(f"/browse?{query_string}")

    def is_ready_to_check(self):
        # Is this search due checking?
        if not self.last_checked_at:
            return True
        return (self.last_checked_at + self.check_every) < timezone.now()
