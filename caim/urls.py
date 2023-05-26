"""caim URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from caim_base.views import (account_details, animal, auth, awg, browse,
                             comments, fosterer_profile, home, saved_search,
                             saved_search_email_notifications, shortlist,
                             user_profile)
from caim_base.views.utils import user_csv_download

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home.index, name="home"),
    path("browse", browse.view, name="browse"),
    path("animal/<animal_id>", animal.view, name="animal"),
    path(
        "my-organizations",
        user_profile.my_organizations,
        name="user_profile_my_organizations",
    ),
    path("fosterer/<stage_id>", fosterer_profile.edit),
    path("fosterer", fosterer_profile.start),
    path("register", auth.register_view, name="register"),
    path("login", auth.login_view, name="login"),
    path(
        "login/", auth.login_view, name="login_with_slash"
    ),  # @todo fix trailing slash issues
    path("logout", auth.logout_view, name="logout"),
    path("api/shortlist", shortlist.api, name="shortlist_api"),
    path("api/saved-search/add", saved_search.add, name="saved_search_add"),
    path(
        "api/saved-search/send-emails",
        saved_search_email_notifications.send_saved_search_email_notifications,
        name="saved_search_send_emails",
    ),
    path("avatar/", include("avatar.urls")),
    path("comments/add", comments.add),
    path("comments/<comment_id>/edit", comments.edit),
    path("comments/<comment_id>/delete", comments.delete),
    path("comments/<int:comment_id>/reply", comments.CreateSubComment.as_view()),
    path("reply/<int:pk>/edit", comments.SubCommentEditView.as_view()),
    path("reply/<int:pk>/delete", comments.SubCommentDeleteView.as_view()),
    path("user/details", account_details.view, name="account_details"),
    path("user/details/edit", account_details.edit, name="account_details_edit"),
    path("user/<username>", user_profile.view),
    path("user/<username>/edit", user_profile.edit, name="user_edit"),
    path("organization/apply", awg.create, name="awg_create"),
    path("organization/<awg_id>/edit", awg.edit, name="awg_edit"),
    path("organization/<awg_id>/animals", awg.list_animals, name="awg_list_animals"),
    path(
        "organization/<awg_id>/animals/add",
        awg.add_animal,
        name="awg_add_animal",
    ),
    path(
        "organization/<awg_id>/animals/import",
        awg.import_animal,
        name="awg_import_animal",
    ),
    path(
        "organization/<awg_id>/animals/<animal_id>",
        awg.edit_animal,
        name="awg_edit_animal",
    ),
    path(
        "organization/<awg_id>/animals/<animal_id>/photos",
        awg.animal_photos,
        name="awg_animal_photos",
    ),
    path(
        "organization/<awg_id>/animals/<animal_id>/publish",
        awg.publish_animal,
        name="awg_animal_publish",
    ),
    path("organization/<awg_id>/members", awg.list_members, name="awg_list_members"),
    path("organization/<awg_id>/members/add", awg.add_member, name="awg_add_member"),
    path(
        "organization/<awg_id>/members/update",
        awg.update_member,
        name="awg_update_member",
    ),
    path("organization/<awg_id>", awg.view, name="awg"),
    path("utils/users-csv", user_csv_download.view, name="user_csv_download"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
