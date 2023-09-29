from csvexport.actions import csvexport
from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .admin_widgets import AdminImageMixin
from .models.animals import (
    Animal,
    AnimalComment,
    AnimalImage,
    AnimalSubComment,
    Awg,
    Breed,
    User,
)
from .models.awg import AwgMember
from .models.fosterer import FostererProfile, FosterApplication, FostererReferenceDetail
from .models.user import UserProfile

# Unregister the user admin so we can user our own
admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fields = ("city", "state", "zip_code", "description")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    actions = [csvexport]
    list_display = ("email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser")
    inlines = [
        UserProfileInline,
    ]


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


class ReferenceInline(admin.TabularInline):
    model = FostererReferenceDetail


class CommentAdmin(admin.ModelAdmin):
    inlines = [SubCommentInline]


class FostererProfileAdmin(admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = [x.name for x in FostererProfile._meta.fields if x.editable and
                         not x.is_relation and
                         not x.primary_key and not getattr(x, 'system_check_deprecated_details')]

    inlines = [ReferenceInline]


admin.site.register(Breed)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(Awg, AwgAdmin)
admin.site.register(AnimalComment, CommentAdmin)
admin.site.register(FostererProfile, FostererProfileAdmin)
admin.site.register(FosterApplication)
