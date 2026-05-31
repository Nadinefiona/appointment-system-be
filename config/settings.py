from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


def _csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


DEBUG = config("DEBUG", default=True, cast=bool)

_secret = (config("SECRET_KEY", default="") or "").strip()
SECRET_KEY = _secret or "django-insecure-dev-only-set-a-real-secret-key-for-production"

ALLOWED_HOSTS = _csv(config("ALLOWED_HOSTS", default="localhost,127.0.0.1"))
_render_host = config("RENDER_EXTERNAL_HOSTNAME", default="").strip()
if _render_host:
    ALLOWED_HOSTS.append(_render_host)

CSRF_TRUSTED_ORIGINS = _csv(config("CSRF_TRUSTED_ORIGINS", default=""))
if _render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_render_host}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
    "apps.accounts.apps.AccountsConfig",
    "apps.providers.apps.ProvidersConfig",
    "apps.services.apps.ServicesConfig",
    "apps.bookings.apps.BookingsConfig",
    "apps.core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

_database_url = config("DATABASE_URL", default="").strip()
if _database_url:
    DATABASES = {
        "default": dj_database_url.parse(_database_url, conn_max_age=600),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("POSTGRES_DB", default="appointment_system_db"),
            "USER": config("POSTGRES_USER", default="postgres"),
            "PASSWORD": config("POSTGRES_PASSWORD", default=""),
            "HOST": config("POSTGRES_HOST", default="localhost"),
            "PORT": config("POSTGRES_PORT", default="5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Appointment System API",
    "DESCRIPTION": "JWT auth. Use Authorize with Bearer access token.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
        "displayRequestDuration": True,
    },
    "TAGS": [
        {"name": "Authentication"},
        {"name": "Registration"},
        {"name": "Account"},
        {"name": "Providers"},
        {"name": "Services"},
        {"name": "Availability"},
        {"name": "Bookings"},
        {"name": "Admin"},
    ],
}

CORS_ALLOWED_ORIGINS = _csv(
    config("CORS_ALLOWED_ORIGINS", default="http://localhost:3000,http://127.0.0.1:3000")
)
CORS_ALLOW_CREDENTIALS = True

EMAIL_NOTIFICATIONS_ENABLED = config("EMAIL_NOTIFICATIONS_ENABLED", default=True, cast=bool)
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="").strip()
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="").replace(" ", "").strip()
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="").strip() or EMAIL_HOST_USER or "noreply@appointments.local"
EMAIL_FAIL_SILENTLY = config("EMAIL_FAIL_SILENTLY", default=False, cast=bool)

BOOKING_DEFAULT_MINUTES = config("BOOKING_DEFAULT_MINUTES", default=60, cast=int)
BOOKING_REMINDER_HOURS = config("BOOKING_REMINDER_HOURS", default=24, cast=int)
BOOKING_REMINDER_WINDOW_MINUTES = config("BOOKING_REMINDER_WINDOW_MINUTES", default=30, cast=int)

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
