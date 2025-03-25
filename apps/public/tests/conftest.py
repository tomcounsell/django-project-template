"""
Pytest configuration for the public app tests.

This file contains fixtures and configuration for the public app tests.
"""

import os
import sys
import pytest
from django.test import override_settings

# Add 'testserver' to ALLOWED_HOSTS for client tests
@pytest.fixture(autouse=True, scope="session")
def allowed_hosts_setup():
    """Configure ALLOWED_HOSTS to include 'testserver' for tests."""
    with override_settings(
        ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"]
    ):
        yield