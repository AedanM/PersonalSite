from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("images/favicon.png"))),
    path("iterlink", views.iterLink, name="iterLink"),
    path(route="refresh", view=views.refresh, name="Refresh"),
    path("tools", views.tools, name="tools"),
    path("log", views.Log, name="log"),
    path("", views.index, name="index"),
]
