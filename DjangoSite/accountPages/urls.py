from django.urls import path

from . import views

urlpatterns = [
    path(route="login/", view=views.loginView),
    path(route="logout/", view=views.logoutView),
]
