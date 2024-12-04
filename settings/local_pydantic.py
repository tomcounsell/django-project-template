# settings/local.py
from .pydantic_settings import settings  # Import Pydantic-validated settings

SECRET_KEY = settings.SECRET_KEY

INTERNAL_IPS = settings.INTERNAL_IPS

DATABASES = {
    "default": {
        "ENGINE": settings.DATABASES_ENGINE,
        "NAME": settings.DATABASES_NAME,
        "USER": settings.DATABASES_USER,
        "PASSWORD": settings.DATABASES_PASSWORD,
        "HOST": settings.DATABASES_HOST,
        "PORT": settings.DATABASES_PORT,
    }
}

# CACHES settings using Redis URL
REDIS_URL = settings.REDIS_URL
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# AWS settings
AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

AWS_OPTIONS = {
    "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
    "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
    "AWS_STORAGE_BUCKET_NAME": AWS_STORAGE_BUCKET_NAME,
}

AWS_SNS_NAME = settings.AWS_SNS_NAME
AWS_STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"

# OAUTH AND SOCIAL settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET

# OPENAI settings
OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_RETRY_ATTEMPTS = settings.OPENAI_RETRY_ATTEMPTS
OPENAI_RETRY_WAIT_MULTIPLIER = settings.OPENAI_RETRY_WAIT_MULTIPLIER
OPENAI_RETRY_WAIT_MIN = settings.OPENAI_RETRY_WAIT_MIN
OPENAI_RETRY_WAIT_MAX = settings.OPENAI_RETRY_WAIT_MAX

# LOGGING configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": settings.LOGGING_FORMAT,
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": settings.LOGGING_LEVEL,
            "propagate": True,
        },
        "apps.insights": {
            "handlers": ["console"],
            "level": settings.LOGGING_LEVEL,
            "propagate": False,
        },
    },
}

# Adjustable time delay for scheduling the summaries task chain (in seconds)
SUMMARY_TASK_TIME_DELAY = settings.SUMMARY_TASK_TIME_DELAY
