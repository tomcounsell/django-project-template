import os

from settings import LOCAL, STAGE, DEMO, PRODUCTION

# STATIC FILES
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = DEFAULT_FILE_STORAGE


# AWS
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', "")
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', "")
AWS_STORAGE_BUCKET_NAME = AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME', "")
AWS_OPTIONS = {
    'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID,
    'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY,
    'AWS_STORAGE_BUCKET_NAME': AWS_S3_BUCKET_NAME,
}
AWS_DEFAULT_ACL = 'public-read'
AWS_SNS_NAME = os.environ.get('AWS_SNS_NAME', "")
AWS_STATIC_URL = 'https://' + AWS_S3_BUCKET_NAME + '.s3.amazonaws.com/'


if not LOCAL:
    STATIC_URL = AWS_STATIC_URL

CACHES = {
    "default": {
         "BACKEND": "redis_cache.RedisCache",
         "LOCATION": os.environ.get('REDIS_URL'),
    }
}



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# HEROKU DATABASE
import dj_database_url
DATABASES = {'default': dj_database_url.config(), }
# Set DATABASE_URL in config if using other host
# DATABASE_URL = f"postgresql://{username}:{password}@{host}:5432/{dbname}"


DEFAULT_FROM_EMAIL = "info@example.com"  # if you don't already have this in settings
SERVER_EMAIL = "info@example.com"  # ditto (default from-email for Django errors)

# GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-1234567-8'
# FACEBOOK_PIXEL_ID = '1234567890'
# HUBSPOT_PORTAL_ID = '1234'
# HUBSPOT_DOMAIN = 'somedomain.web101.hubspot.com'
# INTERCOM_APP_ID = '0123456789abcdef0123456789abcdef01234567'
# OPTIMIZELY_ACCOUNT_NUMBER = '1234567'
