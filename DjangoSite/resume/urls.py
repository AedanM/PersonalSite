from django.urls import path

from . import views

urlpatterns = [
    path("pdf", views.pdf, name="resume"),
    path("", views.resume, name="resume"),
]
