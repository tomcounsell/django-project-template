"""
Pytest configuration for behavior tests.

This module provides pytest fixtures and configuration for
testing behavior mixins. It's used for running the test_behaviors
package tests in isolation, without loading the entire Django project.

Note: When running tests with the main project's pytest configuration,
this module is NOT used, as pytest will use the root conftest.py and
settings are already configured.
"""

import os
import warnings
import django
from django.conf import settings


def pytest_configure():
    """Configure Django settings for isolated behavior tests."""
    # Only configure if Django settings aren't already configured
    if not settings.configured:
        # Show warning about recommended test method
        warnings.warn(
            "Running behavior tests in isolation uses SQLite. "
            "For compatibility with JSON fields, run tests with: "
            "DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_behaviors/",
            UserWarning
        )
        
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