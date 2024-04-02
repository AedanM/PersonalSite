from django.urls import path

from . import views

urlpatterns = [
    path("update", views.update, name="update"),
    path("new", views.new, name="new"),
    path("", views.index, name="index"),
]
