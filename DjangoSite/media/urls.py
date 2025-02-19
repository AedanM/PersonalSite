# pylint: disable=C0103
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path(route="delete", view=views.delete, name="delete"),
    path(route="new", view=views.new, name="new"),
    path(route="edit", view=views.edit, name="edit"),
    path(route="", view=views.index, name="index"),
    path(route="wiki", view=views.wikiLoad, name="wikiLoad"),
    path(route="setBool", view=views.SetBool, name="setBool"),
    path(route="view", view=views.viewMedia, name="view"),
    path(route="fullView", view=views.fullView, name="pagedView"),
    path(route="check", view=views.checkFiles, name="checkInfo"),
    path(route="stats", view=views.stats, name="Stats"),
    path(route="refresh", view=views.refresh, name="Refresh"),
    path(route="backup.json", view=views.backup, name="backup"),
    path(route="adjustTags", view=views.adjustTags, name="adjustTags"),
    path(route="api", view=views.apiRedirect, name="apiCall"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
