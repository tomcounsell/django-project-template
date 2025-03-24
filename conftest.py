"""
Pytest configuration for the project.

This file configures pytest for running Django tests with proper
database setup and fixtures.
"""

import os
import django
import pytest
from django.conf import settings


def pytest_configure():
    """Configure Django for pytest if not already done."""
    # Check if Django is already configured
    if not settings.configured:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
        django.setup()


@pytest.fixture(scope="session")
def django_db_setup():
    """Configure database for testing."""
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("TEST_DB_NAME", "test_django_project"),
            "USER": os.environ.get("TEST_DB_USER", "postgres"),
            "PASSWORD": os.environ.get("TEST_DB_PASSWORD", "postgres"),
            "HOST": os.environ.get("TEST_DB_HOST", "localhost"),
            "PORT": os.environ.get("TEST_DB_PORT", "5432"),
            "CONN_MAX_AGE": 0,
        }
    }
