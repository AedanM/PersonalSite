from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("images/favicon.png"))),
    path("iterlink", views.IterLink, name="iterLink"),
    path(route="refresh", view=views.Refresh, name="Refresh"),
    path("tools", views.ToolsPage, name="tools"),
    path("log", views.Log, name="log"),
    path(route="blog", view=views.BlogHome, name="blogHome"),
    path(route="blog/<str:path>", view=views.BlogPages, name="blog"),
    path("", views.Index, name="index"),
]
