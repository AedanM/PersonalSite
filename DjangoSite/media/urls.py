from django.urls import path

from . import views

urlpatterns = [
    path("update", views.update, name="update"),
    path("", views.index, name="index"),
]
