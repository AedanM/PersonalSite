"""URL configuration for DjangoSite project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("landing.urls")),
    path("accounts/", include("accountPages.urls")),
    path("admin/", admin.site.urls),
    path("media/", include("media.urls")),
    path("resume/", include("resume.urls")),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]
