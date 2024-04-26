from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("images/favicon.png"))),
]
