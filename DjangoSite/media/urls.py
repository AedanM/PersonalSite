# pylint: disable=C0103
from django.urls import path

from . import views

urlpatterns = [
    path(route="update", view=views.update, name="update"),
    path(route="new", view=views.new, name="new"),
    path(route="edit", view=views.edit, name="edit"),
    path(route="", view=views.index, name="index"),
    path(route="wiki", view=views.wikiScrape, name="wikiScrape"),
    path(route="setBool", view=views.SetBool, name="setBool"),
    path(route="view", view=views.viewMedia, name="view"),
]
