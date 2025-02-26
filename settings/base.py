# from __future__ import absolute_import
import mimetypes
import os
from pathlib import Path
import socket

# DEFINE THE ENVIRONMENT TYPE
PRODUCTION = STAGE = DEMO = LOCAL = False
dt_key = os.environ.get('DEPLOYMENT_TYPE', "LOCAL")
if dt_key == 'PRODUCTION':
    PRODUCTION = True
elif dt_key == 'DEMO':
    DEMO = True
elif dt_key == 'STAGE':
    STAGE = True
else:
    LOCAL = True

DEBUG = LOCAL or STAGE
BASE_DIR = Path(__file__).resolve().parent.parent
SITE_ROOT = BASE_DIR

WSGI_APPLICATION = 'settings.wsgi.application'

ALLOWED_HOSTS = [
    # '.mycompany.com',
    # '.herokuapp.com',
    # '.amazonaws.com',
    'localhost',
    '127.0.0.1',
]

if LOCAL:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_WHITELIST = [
        # 'https://myproject-api*.herokuapp.com',
        # 'https://*.mycompany.com',
        # 'https://s3.amazonaws.com',
        # 'https://vendor_api.com',
        'https://localhost',
        'https://127.0.0.1',
    ]

if PRODUCTION:
    HOSTNAME = "app.mycompany.com"
elif STAGE:
    HOSTNAME = "stage.mycompany.com"
else:
    try:
        HOSTNAME = socket.gethostname()
    except:
        HOSTNAME = 'localhost'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# APPLICATIONS
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django_components.safer_staticfiles",  # replaces "django.contrib.staticfiles",
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
    "django_components",
]

APPS = [
    'apps.common',
    # 'apps.integration',
    'apps.communication',
    'apps.public',  # for web front-end
    # 'apps.api',  # for API
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + APPS
SITE_ID = 1

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

LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/account/login"

ROOT_URLCONF = "settings.urls"

# DATABASES -> SEE VENDOR OR LOCAL SETTINGS

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "apps" / "public" / "templates",
        ],
        # "APP_DIRS": True,  # removed for django-components
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
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "django_components.template_loader.Loader",
                    ],
                )
            ],
            "builtins": [
                "django_components.templatetags.component_tags",
            ],
        },
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
# Additional locations of static files
STATICFILES_DIRS = [
    # BASE_DIR / "static",
    BASE_DIR / "apps" / "public" / "static",
]

# Django Components settings
COMPONENTS_DIRS = [
    BASE_DIR / "apps" / "public" / "views" / "components",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

mimetypes.add_type("text/javascript", ".js", True)
mimetypes.add_type("text/css", ".css", True)

WSGI_APPLICATION = "settings.wsgi.application"

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

# https://django-request.readthedocs.io/en/latest/settings.html#request-ignore-paths
REQUEST_IGNORE_PATHS = (
    r'^admin/',
)

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_L10N = False
USE_TZ = True

AUTH_USER_MODEL = "common.User"
LOGIN_URL = "/account/login"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# General apps settings
if PRODUCTION or STAGE:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
