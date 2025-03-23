"""
Tests for the Loops shortcuts.
"""
from unittest import mock

from django.test import TestCase

from apps.common.models import User
from apps.integration.loops.shortcuts import send_password_reset_email


class LoopsShortcutsTestCase(TestCase):
    """Test case for the Loops shortcuts."""

    def setUp(self):
        """Set up the test case."""
        self.user = mock.Mock(spec=User)
        self.user.email = "test@example.com"

    @mock.patch("apps.integration.loops.shortcuts.LoopsClient")
    def test_send_password_reset_email(self, mock_client_class):
        """Test the send_password_reset_email function."""
        # TODO: Implement test for send_password_reset_email