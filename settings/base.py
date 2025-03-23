"""
Core Django settings common to all environments.
"""
import mimetypes
import os
from pathlib import Path

from settings.env import BASE_DIR, DEBUG, LOCAL, PRODUCTION, STAGE, HOSTNAME

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "storages",
    "django_extensions",
    # "request", # a statistics module for django. It stores requests in a database for admins to see.
    # "django_user_agents",
    'debug_toolbar',
    "widget_tweaks",
    "rest_framework",
    "rest_framework_api_key",
    "django_filters",
    "django_htmx",
]

PROJECT_APPS = [
    'apps.common',
    # 'apps.integration',
    'apps.communication',
    'apps.public',  # for web front-end
    # 'apps.api',  # for API
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS
SITE_ID = 1

# Middleware configuration
MIDDLEWARE = [
    "apps.common.utilities.django.middleware.APIHeaderMiddleware",
    # "django_user_agents.middleware.UserAgentMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # "request_logging.middleware.LoggingMiddleware",
    # "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # "request.middleware.RequestMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

# URL configuration
ROOT_URLCONF = "settings.urls"
WSGI_APPLICATION = "settings.wsgi.application"

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "apps" / "public" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                # 'django.template.context_processors.media',
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.static",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Static files and media
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    # BASE_DIR / "static",
    BASE_DIR / "apps" / "public" / "static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

mimetypes.add_type("text/javascript", ".js", True)
mimetypes.add_type("text/css", ".css", True)

# Authentication settings
AUTH_USER_MODEL = "common.User"
LOGIN_URL = "/account/login"
LOGIN_REDIRECT_URL = "/"

# Password validation
PASSWORD_RESET_TIMEOUT_DAYS = 7
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_L10N = False
USE_TZ = True

# Default primary key field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Request settings
REQUEST_IGNORE_PATHS = (
    r'^admin/',
)

# SSL settings for production
if PRODUCTION or STAGE:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50,
}