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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from caim_base.views import (
    home,
    shortlist,
    auth,
    animal,
    browse,
    comments,
    user_profile,
    awg,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home.index, name="home"),
    path("browse", browse.view, name="browse"),
    path("animal/<animal_id>", animal.view, name="animal"),
    path("register", auth.register_view, name="register"),
    path("login", auth.login_view, name="login"),
    path("logout", auth.logout_view, name="logout"),
    path("api/shortlist", shortlist.api, name="shortlist_api"),
    path("avatar/", include("avatar.urls")),
    path("comments/add", comments.add),
    path("comments/<comment_id>/edit", comments.edit),
    path("comments/<comment_id>/delete", comments.delete),
    path("user/<username>", user_profile.view),
    path("user/<username>/edit", user_profile.edit),
    path("awg/<awg_id>", awg.view, name="awg"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
