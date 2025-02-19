# pylint:disable=C0103
"""
ASGI config for DjangoSite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from pathlib import Path

from blacknoise import BlackNoise
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
    ]
)

application = BlackNoise(base_application)
BASE_DIR = Path(__file__).parent.parent
application.add(BASE_DIR / "static", "/static")
