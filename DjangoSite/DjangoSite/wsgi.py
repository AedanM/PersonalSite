# pylint:disable=C0103
"""
WSGI config for DjangoSite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoSite.settings")

application = WhiteNoise(get_wsgi_application(), autorefresh=True)
