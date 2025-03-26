"""
Settings for third-party services and integrations.
"""
import os

from settings.env import LOCAL

# AWS configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', "")
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', "")
AWS_STORAGE_BUCKET_NAME = AWS_S3_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', "")
AWS_OPTIONS = {
    'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID,
    'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY,
    'AWS_STORAGE_BUCKET_NAME': AWS_S3_BUCKET_NAME,
}
AWS_DEFAULT_ACL = 'public-read'
AWS_SNS_NAME = os.environ.get('AWS_SNS_NAME', "")
AWS_STATIC_URL = f'https://{AWS_S3_BUCKET_NAME}.s3.amazonaws.com/' if AWS_S3_BUCKET_NAME else ""

# S3 for static files in production
if not LOCAL and AWS_S3_BUCKET_NAME:
    STATIC_URL = AWS_STATIC_URL
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = DEFAULT_FILE_STORAGE

# Email configuration
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.com")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "server@example.com")

# Loops integration
LOOPS_API_KEY = os.environ.get("LOOPS_API_KEY", "")

# Twilio integration
TWILIO_ENABLED = os.environ.get("TWILIO_ENABLED", "False").lower() == "true"
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")

# Social Auth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')