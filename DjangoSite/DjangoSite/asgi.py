"""ASGI config for DjangoSite project."""

import os

from blacknoise import BlackNoise
from django.conf import settings as django_settings
from django.core.asgi import get_asgi_application
from media.API.Routes import API_APP
from starlette.applications import Starlette
from starlette.routing import Mount

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoSite.settings")

django_app = get_asgi_application()


# Combine both apps with routing
base_application = Starlette(
    routes=[
        Mount("/media/api", app=API_APP),
        Mount("/", app=django_app),
    ],
)

application = BlackNoise(base_application)
application.add(django_settings.EXTERNAL_DIR / "static", "/static")
application.add(django_settings.SYNC_PATH / "blog" / "attachments", "/attachments")
