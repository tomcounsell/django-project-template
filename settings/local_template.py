# Need to explicitly import os here as it's used by the env var lookups
import os

# SECURITY WARNING: keep the secret key used in production secret!
# Generate a new secret key using:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY = os.environ.get('SECRET_KEY', '50 char security key here')

INTERNAL_IPS = [
    "127.0.0.1",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'local_postgres_db_name'),
        'USER': os.environ.get('DB_USER', 'local_postgres_username'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'local_postgres_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
# OR USE REDIS LOCALLY
# REDIS_URL = "redis://127.0.0.1:6379/5"
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": REDIS_URL,
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         },
#     }
# }

LOOPS_API_KEY = os.environ.get('LOOPS_API_KEY', '')

# AWS
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = AWS_S3_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'project-stage')
AWS_OPTIONS = {
    'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID,
    'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY,
    'AWS_STORAGE_BUCKET_NAME': AWS_S3_BUCKET_NAME,
}
AWS_SNS_NAME = os.environ.get('AWS_SNS_NAME', '')
AWS_STATIC_URL = 'https://' + AWS_S3_BUCKET_NAME + '.s3.amazonaws.com/'

# OAUTH AND SOCIAL
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')
