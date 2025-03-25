import pytest
from django.conf import settings


@pytest.fixture(scope='session', autouse=True)
def set_test_settings():
    """Configure settings for API tests"""
    # Add 'testserver' to ALLOWED_HOSTS
    settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']
    
    # Return settings for potential use in tests
    return settings