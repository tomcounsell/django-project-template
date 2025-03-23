import os
import django
from django.conf import settings

def pytest_configure():
    # Setup minimal Django settings for tests
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'apps.common',
        ],
        AUTH_USER_MODEL='auth.User',
        SECRET_KEY='fakesecretkey',
        MIDDLEWARE=[],
        ROOT_URLCONF=[],
    )
    django.setup()