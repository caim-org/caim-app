import io

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from caim_base.utils import (draw_pdf_checkbox, draw_pdf_choices,
                             draw_pdf_divider, draw_pdf_field, draw_pdf_header,
                             draw_pdf_label, draw_pdf_long_field,
                             draw_pdf_page_num, draw_pdf_title, font_name,
                             header_font_name, init_pdf)
from typing import List, Optional
from caim_base.models.animals import Animal

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
        HOUSE_POTTY = "HOUSE_POTTY", "House / potty training"
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
        blank=True, null=True, default=None,
        verbose_name='Which type of animal(s) are you wanting to foster?'
    )
    category_of_animals = ChoiceArrayField(
        models.CharField(max_length=32, choices=CategoryOfAnimals.choices),
        blank=True, null=True, default=None,
        verbose_name='Please check any / all that you\'re interested in fostering?'
    )
    behavioural_attributes = ChoiceArrayField(
        models.CharField(max_length=32, choices=BehaviouralAttributes.choices),
        blank=True, null=True, default=None,
        verbose_name='Please check any of the requirements you have for a foster'
    )
    timeframe = models.CharField(
        choices=Timeframe.choices,
        max_length=32, blank=False, null=True, default=None,
        verbose_name='Please let us know which timeframe you\'re available for fostering'
    )
    timeframe_other = models.TextField(
        blank=True, null=True, default=None,
        verbose_name="If 'other', please give details"
    )
    num_existing_pets = models.IntegerField(
        blank=True, null=True, default=None,
        verbose_name='How many pets do you currently have in your home?'
    )
    existing_pets_details = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='Please give details of your existing pets'
    )
    experience_description = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='Please describe your experience with animals (personal pets, training, interactions, etc.)'
    )
    experience_categories = ChoiceArrayField(
        models.CharField(max_length=32, choices=ExperienceCategories.choices),
        blank=True, null=True, default=None,
        verbose_name='Do you have experience with any of the following? Check all that apply.'
    )
    experience_given_up_pet = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='Have you ever given a pet up? If so, please describe the situation.'
    )
    reference_1 = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='Reference #1'
    )
    reference_2 = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='Reference #2'
    )
    reference_3 = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='Reference #3'
    )
    people_at_home = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='Please list how many people live in your home and their ages'
    )
    yard_type = models.CharField(
        choices=YardTypes.choices,
        max_length=32, blank=False, null=True, default=None,
        verbose_name='Describe your yard'
    )
    yard_fence_over_5ft = models.CharField(
        choices=YesNo.choices,
        max_length=32, blank=False, null=True, default=None,
        verbose_name='If your yard is fully fenced, is it all over 5 feet tall?'
    )
    rent_own = models.CharField(
        choices=RentOwn.choices,
        max_length=32, blank=False, null=True, default=None,
        verbose_name='Do you rent or own?'
    )
    rent_restrictions = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='If you rent, please describe any pet restrictions that are in place.'
    )
    rent_ok_foster_pets = models.CharField(
        choices=YesNo.choices,
        max_length=32, blank=False, null=True, default=None,
        verbose_name='If you rent, is your landlord ok with you having foster pets?',
    )
    hours_alone_description = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='How many hours per day will your foster animal be left alone?'
    )
    hours_alone_location = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='Where will your foster animal be when they\'re left alone?'
    )
    sleep_location = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='Where will your foster animal sleep?'
    )
    other_info = models.TextField(
        blank=True, null=True, default=None,
        verbose_name='Is there anything else you want us / rescues to know?'
    )
    ever_been_convicted_abuse = models.CharField(
        choices=YesNo.choices,
        max_length=32, blank=False, null=True, default=None,
        verbose_name='Have you or a family / household member ever been convicted of an animal related crime (animal abuse, neglect, abandonment, etc.)?'
    )
    agree_share_details = models.CharField(
        choices=YesNo.choices,
        max_length=32, blank=False, null=True, default=None,
        verbose_name='Do you agree that we can share the details you\'ve provided with rescues in your area?'
    )
    is_complete = models.BooleanField(default=False)

def __str__(self) -> str:
    return f"{self.firstname} {self.lastname}"

def query_fostererprofiles(
    behavioural_attributes: Optional[List[str]] = None,
    is_complete=True,
    sort: Optional[str | List[str]] = ["firstname" , "lastname"],
) -> models.QuerySet:
    """
      Query fosterer profiles with preferred defaults  
    """

    query = FostererProfile.objects.all()

    
    if behavioural_attributes:
        query = query.filter(behavioural_attributes__contains=behavioural_attributes)

    if is_complete:
        query = query.filter(is_complete=True)

    if sort is not None:
        if isinstance(sort, list):
            for s in sort:
                query = query.order_by(s)
        else:
            query = query.order_by(sort)

    return query


class FosterApplication(models.Model):
    
    class FosterApplicationStatus(models.TextChoices):
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        PENDING = "PENDING", "Pending"

    fosterer = models.ForeignKey(FostererProfile, on_delete=models.CASCADE, related_name="applications")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=32, choices=FosterApplicationStatus.choices)
    reject_reason = models.TextField(max_length=65516, null=True, blank=True)
    submitted_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)
    
    def __str__(self) -> str:
        return f"Application for {self.animal} by {self.fosterer}"