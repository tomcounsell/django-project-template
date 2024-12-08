# settings/local.py
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

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

# Redis settings
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_DB = os.environ.get("REDIS_DB", "5")
REDIS_URL = os.environ.get("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
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

# OAUTH AND SOCIAL settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("GOOGLE_OAUTH2_KEY", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("GOOGLE_OAUTH2_SECRET", "")

# OpenAI settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_RETRY_ATTEMPTS = int(os.environ.get("OPENAI_RETRY_ATTEMPTS", "3"))
OPENAI_RETRY_WAIT_MULTIPLIER = int(os.environ.get("OPENAI_RETRY_WAIT_MULTIPLIER", "1"))
OPENAI_RETRY_WAIT_MIN = int(os.environ.get("OPENAI_RETRY_WAIT_MIN", "2"))
OPENAI_RETRY_WAIT_MAX = int(os.environ.get("OPENAI_RETRY_WAIT_MAX", "10"))

# LOGGING configuration
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
            "level": "DEBUG",
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
        "apps.insights": {
            "handlers": ["console"],
            "level": os.environ.get("LOGGING_LEVEL", "DEBUG"),
            "propagate": False,
        },
    },
}

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,  # Optional: Always show toolbar
}

# Task settings
SUMMARY_TASK_TIME_DELAY = int(os.environ.get("SUMMARY_TASK_TIME_DELAY", "1"))
