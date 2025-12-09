import json
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

EXTERNAL_DIR = Path(r"/home/aedan/External")

LOGIN_REDIRECT_URL = "/"  # new
DJANGO_CONFIG_DICT = json.loads((EXTERNAL_DIR / "config.json").read_text(encoding="utf-8"))

SECRET_KEY = DJANGO_CONFIG_DICT["SecretKey"]

DEBUG = DJANGO_CONFIG_DICT["Debug"]


ALLOWED_HOSTS: list = ["127.0.0.1", "aedanm.uk", "192.168.1.99"]
CSRF_TRUSTED_ORIGINS: list = ["https://127.0.0.1", "https://aedanm.uk", "https://192.168.0.44"]

SYNC_PATH = Path()
for path in DJANGO_CONFIG_DICT["SyncPaths"]:
    if Path(path).exists():
        SYNC_PATH = Path(path)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "{name} at {asctime} ({levelname}) :: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "UserLoggerHandle": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": f"Logging/{date.today()} UserLogger.log",
            "formatter": "base",
        },
        "ExtendedHandle": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": f"Logging/{date.today()} Extended.log",
            "formatter": "base",
        },
    },
    "loggers": {
        "UserLogger": {
            "handlers": ["UserLoggerHandle"],
            "level": "INFO",
            "propagate": True,
        },
        "django": {
            "handlers": ["ExtendedHandle"],
            "level": "INFO",
            "propagate": True,
        },
    },
    "root": {
        "handlers": ["ExtendedHandle"],
        "level": "INFO",
    },
}

INSTALLED_APPS = [
    "media.apps.MediaConfig",
    "landing.apps.LandingConfig",
    "resume.apps.ResumeConfig",
    "accountPages.apps.AccountPagesConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "DjangoSite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["landing/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "DjangoSite.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": EXTERNAL_DIR / "db.sqlite3",
    },
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-gb"

TIME_ZONE = "GMT"

USE_I18N = True

USE_TZ = True


STATIC_ROOT = EXTERNAL_DIR / "static"
STATIC_URL = "static/"

STATICFILES_DIRS = [
    EXTERNAL_DIR / "static",
    SYNC_PATH / "blog" / "static",
]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# TODO : Investigate streaming warning
