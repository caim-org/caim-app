import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from leaflet.admin import LeafletGeoAdmin

from .models import Breed, Animal, Awg, AnimalComment, AnimalImage, AwgMember
from .admin_widgets import AdminImageMixin


class AnimalImageInline(AdminImageMixin, admin.StackedInline):
    model = AnimalImage
    extra = 0


class AnimalAdmin(AdminImageMixin, admin.ModelAdmin):
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


class AwgMemberInline(AdminImageMixin, admin.StackedInline):
    model = AwgMember
    extra = 0


class AwgAdmin(LeafletGeoAdmin, admin.ModelAdmin):
    list_display = ("name", "state", "city", "phone", "email")
    # readonly_fields = ["geo_location"]
    inlines = (AwgMemberInline,)


admin.site.register(Breed)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(Awg, AwgAdmin)
admin.site.register(AnimalComment)
