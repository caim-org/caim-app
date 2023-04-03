import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from leaflet.admin import LeafletGeoAdmin
from setuptools import Command
from csvexport.actions import csvexport

from .models.animals import (
    Breed,
    Animal,
    Awg,
    AnimalComment,
    AnimalSubComment,
    AnimalImage,
    User,
)
from .models.awg import AwgMember
from .models.fosterer import FostererProfile
from .admin_widgets import AdminImageMixin


class UserAdmin(admin.ModelAdmin):
    actions = [csvexport]
    list_display = ("email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser")


class AnimalImageInline(AdminImageMixin, admin.StackedInline):
    model = AnimalImage
    extra = 0


class AnimalAdmin(AdminImageMixin, admin.ModelAdmin):
    actions = [csvexport]
    inlines = (AnimalImageInline,)
    list_display = (
        "name",
        "id",
        "admin_image_tag",
        "animal_type",
        "sex",
        "age",
        "primary_breed",
    )
    search_fields = ["name"]
    list_filter = ["animal_type", "awg"]


class AwgMemberInline(AdminImageMixin, admin.StackedInline):
    model = AwgMember
    extra = 0


class AwgAdmin(LeafletGeoAdmin, admin.ModelAdmin):
    actions = [csvexport]
    list_display = ("name", "id", "status", "state", "city", "phone", "email")
    readonly_fields = ["geo_location"]
    inlines = (AwgMemberInline,)
    search_fields = ["name"]
    list_filter = ["status", "state", "city"]


class SubCommentInline(admin.TabularInline):
    model = AnimalSubComment


class CommentAdmin(admin.ModelAdmin):
    inlines = [SubCommentInline]


admin.site.register(Breed)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(Awg, AwgAdmin)
admin.site.register(AnimalComment, CommentAdmin)
admin.site.register(FostererProfile)

# Replace the user admin so we can override things
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
