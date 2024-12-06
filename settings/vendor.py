import os

from settings import LOCAL

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # AWS
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', "")
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', "")
# AWS_STORAGE_BUCKET_NAME = AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME', "")
# AWS_OPTIONS = {
#     'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID,
#     'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY,
#     'AWS_STORAGE_BUCKET_NAME': AWS_S3_BUCKET_NAME,
# }
# AWS_DEFAULT_ACL = 'public-read'
# AWS_SNS_NAME = os.environ.get('AWS_SNS_NAME', "")
# AWS_STATIC_URL = 'https://' + AWS_S3_BUCKET_NAME + '.s3.amazonaws.com/'

# # STATIC FILES
# if not LOCAL:
#     STATIC_URL = AWS_STATIC_URL
#     DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#     STATICFILES_STORAGE = DEFAULT_FILE_STORAGE


DEFAULT_FROM_EMAIL = "admin@investors.royop.com"
SERVER_EMAIL = "admin@investors.royop.com"

LOOPS_API_KEY = os.environ.get("LOOPS_API_KEY")
