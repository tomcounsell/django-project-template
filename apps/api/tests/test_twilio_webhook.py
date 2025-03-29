import json
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.common.models.sms import SMS


@override_settings(DEBUG=True, TWILIO_ENABLED=True)
class TwilioWebhookTestCase(TestCase):
    """Test cases for Twilio webhook handler"""
    
    def setUp(self):
        self.client = APIClient()
        self.webhook_url = reverse('api:twilio-webhook')
        
        # Create test SMS with an external_id
        self.sms = SMS.objects.create(
            to_number="+12345678901",
            from_number="+19876543210",
            body="Test message",
            external_id="SM12345678901234567890123456789012"
        )
    
    def test_webhook_sms_delivered(self):
        """Test webhook updates SMS status to delivered"""
        # Payload similar to what Twilio would send
        payload = {
            "MessageSid": self.sms.external_id,
            "MessageStatus": "delivered",
            "To": self.sms.to_number,
            "From": self.sms.from_number,
        }
        
        # Initially the SMS should not have a status or read_at
        self.assertIsNone(self.sms.status)
        self.assertIsNone(self.sms.read_at)
        
        # Send webhook request
        response = self.client.post(
            self.webhook_url,
            data=payload,
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        
        # Refresh SMS from database
        self.sms.refresh_from_db()
        
        # Verify SMS was updated
        self.assertEqual(self.sms.status, "delivered")
        self.assertIsNotNone(self.sms.read_at)  # Should be marked as read when delivered
    
    def test_webhook_sms_failed(self):
        """Test webhook updates SMS status to failed with error info"""
        # Payload with failed status and error details
        payload = {
            "MessageSid": self.sms.external_id,
            "MessageStatus": "failed",
            "ErrorCode": "30002",
            "ErrorMessage": "Account suspended",
            "To": self.sms.to_number,
            "From": self.sms.from_number,
        }
        
        # Send webhook request
        response = self.client.post(
            self.webhook_url,
            data=payload,
            format='json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        # Refresh SMS from database
        self.sms.refresh_from_db()
        
        # Verify SMS was updated with error information
        self.assertEqual(self.sms.status, "failed")
        self.assertEqual(self.sms.error_code, "30002")
        self.assertEqual(self.sms.error_message, "Account suspended")
        self.assertIsNone(self.sms.read_at)  # Failed messages are not marked as read
    
    def test_webhook_invalid_sid(self):
        """Test webhook handles non-existent SMS SID"""
        # Payload with non-existent SID
        payload = {
            "MessageSid": "SM99999999999999999999999999999999",
            "MessageStatus": "delivered",
        }
        
        # Send webhook request
        response = self.client.post(
            self.webhook_url,
            data=payload,
            format='json'
        )
        
        # Verify error response
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)
    
    def test_webhook_missing_parameters(self):
        """Test webhook validation with missing parameters"""
        # Payload with missing MessageStatus
        payload = {
            "MessageSid": self.sms.external_id,
        }
        
        # Send webhook request
        response = self.client.post(
            self.webhook_url,
            data=payload,
            format='json'
        )
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)