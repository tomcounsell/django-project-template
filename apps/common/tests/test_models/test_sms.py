import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import datetime

from apps.common.models.sms import SMS


class SMSModelTestCase(TestCase):
    """Test case for the SMS model."""

    def setUp(self):
        self.sms = SMS.objects.create(
            to_number="+1234567890",
            from_number="+0987654321",
            body="This is a test SMS message."
        )

    def test_sms_creation(self):
        """Test basic SMS creation."""
        self.assertEqual(self.sms.to_number, "+1234567890")
        self.assertEqual(self.sms.from_number, "+0987654321")
        self.assertEqual(self.sms.body, "This is a test SMS message.")
        
        # Test timestamp fields
        self.assertIsNotNone(self.sms.created_at)
        self.assertIsNotNone(self.sms.modified_at)
        
        # These should be None when first created
        self.assertIsNone(self.sms.sent_at)
        self.assertIsNone(self.sms.read_at)

    def test_mark_as_sent(self):
        """Test marking SMS as sent."""
        # Initially sent_at is None
        self.assertIsNone(self.sms.sent_at)
        
        # Mark as sent
        self.sms.mark_as_sent()
        
        # Now sent_at should have a value
        self.assertIsNotNone(self.sms.sent_at)
        
        # Sent time should be close to now
        now = timezone.now()
        self.assertLess((now - self.sms.sent_at).total_seconds(), 10)  # Within 10 seconds

    def test_mark_as_read(self):
        """Test marking SMS as read."""
        # Initially read_at is None
        self.assertIsNone(self.sms.read_at)
        
        # Mark as read
        self.sms.mark_as_read()
        
        # Now read_at should have a value
        self.assertIsNotNone(self.sms.read_at)
        
        # Read time should be close to now
        now = timezone.now()
        self.assertLess((now - self.sms.read_at).total_seconds(), 10)  # Within 10 seconds

    def test_string_representation(self):
        """Test the string representation of SMS."""
        expected = f"SMS to +1234567890: This is a test SMS message."
        self.assertEqual(str(self.sms), expected)