from django.contrib import admin
from .models import Breed, Animal, Awg, AnimalComment, AnimalImage
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from leaflet.admin import LeafletGeoAdmin


class AnimalImageInline(admin.StackedInline):
    model = AnimalImage
    extra = 0


class AnimalAdmin(admin.ModelAdmin):
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


admin.site.register(Breed)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(Awg, LeafletGeoAdmin)
admin.site.register(AnimalComment)
