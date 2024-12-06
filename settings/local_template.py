# settings/local_template.py
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "50 char security key here")

INTERNAL_IPS = [
    "127.0.0.1",
]

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
    }
}

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#         "LOCATION": "unique-snowflake",
#     }
# }
# OR USE REDIS LOCALLY
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/5")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# AWS
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "project-stage")
AWS_S3_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME
AWS_OPTIONS = {
    "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
    "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
    "AWS_STORAGE_BUCKET_NAME": AWS_S3_BUCKET_NAME,
}
AWS_SNS_NAME = os.environ.get("AWS_SNS_NAME", "")
AWS_STATIC_URL = f"https://{AWS_S3_BUCKET_NAME}.s3.amazonaws.com/"

# OAUTH AND SOCIAL
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("GOOGLE_OAUTH2_KEY", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("GOOGLE_OAUTH2_SECRET", "")

# LOGGING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": os.environ.get("LOGGING_LEVEL", "DEBUG"),
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("LOGGING_LEVEL", "INFO"),
            "propagate": True,
        },
        "apps.insights": {  # App-specific logging
            "handlers": ["console"],
            "level": os.environ.get("LOGGING_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

# Adjustable time delay for scheduling the summaries task chain (in seconds)
SUMMARY_TASK_TIME_DELAY = int(os.environ.get("SUMMARY_TASK_TIME_DELAY", "1"))
