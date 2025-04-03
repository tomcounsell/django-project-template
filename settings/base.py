"""
Core Django settings common to all environments.
"""

import mimetypes

from settings.env import BASE_DIR, LOCAL, PRODUCTION, STAGE

# Detect if we are in a test environment
import sys
TESTING = 'test' in sys.argv or 'pytest' in sys.modules

# Application definition
DJANGO_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
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
    "debug_toolbar",
    "widget_tweaks",
    "rest_framework",
    "rest_framework_api_key",
    "django_filters",
    "django_htmx",
    "tailwind",
    "drf_yasg",
]

PROJECT_APPS = [
    "theme",  # django-tailwind app
    "apps.common",
    "apps.integration",
    "apps.api",
    "apps.public",  # for web front-end
    "apps.ai",  # AI integrations and agents
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS
if LOCAL:
    INSTALLED_APPS += [
        "django_browser_reload",
    ]
SITE_ID = 1

# Middleware configuration
MIDDLEWARE = [
    "apps.common.utilities.django.middleware.APIHeaderMiddleware",
    # "django_user_agents.middleware.UserAgentMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
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
    "django_browser_reload.middleware.BrowserReloadMiddleware",
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
        ],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                # 'django.template.context_processors.media',
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.static",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        # Default Django loader
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                )
            ],
        },
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATICFILES_FINDERS = [
    # Default finders
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (User uploaded files)
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

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

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_L10N = False
USE_TZ = True

# Default primary key field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Request settings
REQUEST_IGNORE_PATHS = (r"^admin/",)

# Template Directories
TEMPLATE_DIRS = [
    BASE_DIR / "templates",
]

# Tailwind CSS settings
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = [
    "127.0.0.1",
]

NPM_BIN_PATH = "npm"

# Import Unfold settings
from settings.unfold import UNFOLD

# SSL settings for production
if PRODUCTION or STAGE:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAdminUser",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 50,
}

# DRF-YASG (Swagger/OpenAPI) settings
SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": True,
    "SECURITY_DEFINITIONS": {
        "Basic": {"type": "basic"},
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
    },
    "DEFAULT_MODEL_RENDERING": "example",
}

# Silence the warning about compat renderers
SWAGGER_USE_COMPAT_RENDERERS = False
