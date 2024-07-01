# pylint: disable=C0103
from django.urls import path

from . import views

urlpatterns = [
    path(route="update", view=views.update, name="update"),
    path(route="new", view=views.new, name="new"),
    path(route="edit", view=views.edit, name="edit"),
    path(route="", view=views.index, name="index"),
    path(route="wiki", view=views.wikiScrape, name="wikiScrape"),
    path(route="setDownloaded", view=views.SetDownloaded, name="setDownloaded"),
    path(route="setWatched", view=views.SetWatched, name="setWatched"),
    path(route="view", view=views.viewMedia, name="view"),
]
