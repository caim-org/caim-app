from django.db import models
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField

from ..states import states

User = get_user_model()

class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.
    Uses Django's Postgres ArrayField
    and a MultipleChoiceField with checkboxes for its formfield.
    """

    def formfield(self, **kwargs):
        defaults = {
            'widget': forms.CheckboxSelectMultiple,
            'form_class': forms.MultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)


class FostererProfile(models.Model):

    class TypeOfAnimals(models.TextChoices):
        DOGS = "DOGS", "Dogs"
        CATS = "CATS", "Cats"

    class CategoryOfAnimals(models.TextChoices):
        ADULT_FEMALE = "ADULT_FEMALE", "Adult female"
        ADULT_MALE = "ADULT_MALE", "Adult male"
        PREGNANT_MOTHER = "PREGNANT_MOTHER", "Pregnant mom"
        MOTHER_WITH_BABIES = "MOTHER_WITH_BABIES", "Mom with nursing babies"
        BABIES = "BABIES", "Puppies / kittens"
        PIT_BULLY_BREEDS = "PIT_BULLY_BREEDS", "Pit and/or Bully breeds"

    class BehaviouralAttributes(models.TextChoices):
        GOOD_WITH_DOGS = "GOOD_WITH_DOGS", "Good with dogs"
        GOOD_WITH_CATS = "GOOD_WITH_CATS", "Good with cats"
        GOOD_WITH_KIDS = "GOOD_WITH_KIDS", "Good with children"
        NO_MEDICAL_ISSUES = "NO_MEDICAL_ISSUES", "No medical issues"
        NO_SPECIAL_NEEDS = "NO_SPECIAL_NEEDS", "No special needs"
        NO_BEHAVIOURAL_NEEDS = "NO_BEHAVIOURAL_NEEDS", "No behavioral issues"

    class Timeframe(models.TextChoices):
        MAX_2_WEEKS = "MAX_2_WEEKS", "Up to 2 weeks"
        MAX_3_MONTHS = "MAX_3_MONTHS", "Up to 3 months"
        ANY_DURATION = "ANY_DURATION", "Any duration"
        OTHER = "OTHER", "Other (please specify)"

    class ExperienceCategories(models.TextChoices):
        HOUSE_POTTY = "YES", "House / potty training"
        CRATE = "CRATE", "Crate training"
        LEASH_WALKING = "LEASH_WALKING", "Challenges with leash / walking"
        JUMPING = "JUMPING", "Jumping"
        HIGH_ENERGY = "HIGH_ENERGY", "High energy"
        OBEDIENCE = "OBEDIENCE", "Basic obedience"
        PUPPIES = "PUPPIES", "Training puppies"
        SEPARATION_ANXIETY = "SEPARATION_ANXIETY", "Separation anxiety"
        FEARS = "FEARS", "Fears / phobias"
        REACTIVITY = "REACTIVITY", "Reactivity"
        FOOD_GUARDING = "FOOD_GUARDING", "Food guarding"
        MEDICAL_ISSUES = "MEDICAL_ISSUES", "Medical issues"
        GERIATRIC = "GERIATRIC", "Geriatric concerns"
        NONE_OF_ABOVE = "NONE_OF_ABOVE", "None of the above"

    class YardTypes(models.TextChoices):
        NO_YARD = "NO_YARD", "No yard"
        UNFENCED = "UNFENCED", "Unfenced yard"
        PARTIALLY_FENCED = "PARTIALLY_FENCED", "Partially fenced yard"
        FULLY_FENCED = "FULLY_FENCED", "Fully fenced yard"
    
    class RentOwn(models.TextChoices):
        RENT = "RENT", "Rent"
        OWN = "OWN", "Own"

    class YesNo(models.TextChoices):
        YES = "YES", "Yes"
        NO = "NO", "No"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(blank=True, null=True, max_length=64, default=None)
    lastname = models.CharField(blank=True, null=True, max_length=64, default=None)
    email = models.EmailField(blank=True, null=True, max_length=255, default=None)
    phone = PhoneNumberField(blank=True, null=True, default=None)
    street_address = models.CharField(blank=True, null=True, max_length=244, default=None)
    city = models.CharField(max_length=32, blank=True, null=True, default=None)
    state = models.CharField(max_length=2, blank=True, null=True, choices=states.items(), default=None)
    zip_code = models.CharField(max_length=16, blank=True, null=True, default=None)
    type_of_animals = ChoiceArrayField(
        models.CharField(max_length=32, choices=TypeOfAnimals.choices), 
        blank=True, null=True, default=None
    )
    category_of_animals = ChoiceArrayField(
        models.CharField(max_length=32, choices=CategoryOfAnimals.choices), 
        blank=True, null=True, default=None
    )
    behavioural_attributes = ChoiceArrayField(
        models.CharField(max_length=32, choices=BehaviouralAttributes.choices), 
        blank=True, null=True, default=None
    )
    timeframe = models.CharField(
        choices=Timeframe.choices,
        max_length=32, blank=True, null=True, default=None, 
    )
    timeframe_other = models.TextField(blank=True, null=True, default=None)
    num_existing_pets = models.IntegerField(blank=True, null=True, default=None)
    existing_pets_details = models.TextField(blank=True, null=True, default=None)
    experience_description = models.TextField(blank=True, null=True, default=None)
    experience_categories = ChoiceArrayField(
        models.CharField(max_length=32, choices=ExperienceCategories.choices), 
        blank=True, null=True, default=None
    )
    experience_given_up_pet = models.TextField(blank=True, null=True, default=None)
    reference_1 = models.TextField(blank=True, null=True, default=None)
    reference_2 = models.TextField(blank=True, null=True, default=None)
    reference_3 = models.TextField(blank=True, null=True, default=None)
    people_at_home = models.TextField(blank=True, null=True, default=None)
    yard_type = models.CharField(
        choices=YardTypes.choices,
        max_length=32, blank=True, null=True, default=None, 
    )
    yard_fence_over_5ft = models.CharField(
        choices=YesNo.choices,
        max_length=32, blank=True, null=True, default=None, 
    )
    rent_own = models.CharField(
        choices=RentOwn.choices,
        max_length=32, blank=True, null=True, default=None, 
    )
    rent_restrictions = models.TextField(blank=True, null=True, default=None)
    rent_ok_foster_pets = models.CharField(
        choices=YesNo.choices,
        max_length=32, blank=True, null=True, default=None, 
    )
    hours_alone_description = models.TextField(blank=True, null=True, default=None)
    hours_alone_location = models.TextField(blank=True, null=True, default=None)
    sleep_location = models.TextField(blank=True, null=True, default=None)
    other_info = models.TextField(blank=True, null=True, default=None)
    ever_been_convicted_abuse = models.CharField(
        choices=YesNo.choices,
        max_length=32, blank=True, null=True, default=None, 
    )
    agree_share_details = models.CharField(
        choices=YesNo.choices,
        max_length=32, blank=True, null=True, default=None, 
    )

