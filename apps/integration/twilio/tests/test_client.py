"""
Unit tests for the TwilioClient
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import override_settings, SimpleTestCase

from apps.integration.twilio.client import TwilioClient


@override_settings(
    DEBUG=True,
    TWILIO_ENABLED=True,
    TWILIO_ACCOUNT_SID="test_sid",
    TWILIO_AUTH_TOKEN="test_token",
    TWILIO_PHONE_NUMBER="+19876543210",
)
class TwilioClientDebugModeTestCase(SimpleTestCase):
    """Test TwilioClient in DEBUG mode"""

    def setUp(self):
        self.client = TwilioClient()

    def test_send_sms_debug_mode(self):
        """Test send_sms in DEBUG mode"""
        result = self.client.send_sms(to_number="+12345678901", body="Test message")
        assert result["success"] is True
        assert result["simulated"] is True
        assert "sid" in result

    def test_verify_phone_number_debug_mode(self):
        """Test verify_phone_number in DEBUG mode"""
        result = self.client.verify_phone_number("+12345678901")
        assert result["success"] is True
        assert result["simulated"] is True
        assert result["valid"] is True

    def test_get_message_status_debug_mode(self):
        """Test get_message_status in DEBUG mode"""
        result = self.client.get_message_status("SM12345")
        assert result["success"] is True
        assert result["simulated"] is True
        assert result["status"] == "delivered"


@override_settings(
    DEBUG=False,
    TWILIO_ENABLED=True,
    TWILIO_ACCOUNT_SID="test_sid",
    TWILIO_AUTH_TOKEN="test_token",
    TWILIO_PHONE_NUMBER="+19876543210",
)
class TwilioClientLiveTestCase(SimpleTestCase):
    """Test TwilioClient in live mode with mocked API calls"""

    def setUp(self):
        # Create patch for TwilioRestClient
        self.twilio_client_patcher = patch("twilio.rest.Client")
        self.mock_twilio_client_cls = self.twilio_client_patcher.start()
        self.mock_twilio_client = MagicMock()
        self.mock_twilio_client_cls.return_value = self.mock_twilio_client

        # Create the client after patching
        self.client = TwilioClient()

    def tearDown(self):
        self.twilio_client_patcher.stop()

    def test_send_sms_success(self):
        """Test successful SMS sending"""
        # Setup mock message object
        mock_message = MagicMock()
        mock_message.sid = "SM12345"
        mock_message.status = "queued"

        # Setup mock messages.create method
        self.mock_twilio_client.messages.create.return_value = mock_message

        # Call send_sms method
        result = self.client.send_sms(to_number="+12345678901", body="Test message")

        # Verify result and method call
        assert result["success"] is True
        assert "data" in result

        # Verify Twilio API was called with correct parameters
        self.mock_twilio_client.messages.create.assert_called_once_with(
            to="+12345678901", body="Test message", from_="+19876543210"
        )

    def test_send_sms_with_status_callback(self):
        """Test SMS sending with status callback URL"""
        # Setup mock
        mock_message = MagicMock()
        mock_message.sid = "SM12345"
        self.mock_twilio_client.messages.create.return_value = mock_message

        # Call send_sms with status_callback
        result = self.client.send_sms(
            to_number="+12345678901",
            body="Test message",
            status_callback="https://example.com/webhook",
        )

        # Verify Twilio API was called with status_callback
        self.mock_twilio_client.messages.create.assert_called_once_with(
            to="+12345678901",
            body="Test message",
            from_="+19876543210",
            status_callback="https://example.com/webhook",
        )

    def test_send_sms_error(self):
        """Test error handling in send_sms"""
        # Setup mock to raise exception
        self.mock_twilio_client.messages.create.side_effect = Exception("Test error")

        # Call send_sms method
        result = self.client.send_sms(to_number="+12345678901", body="Test message")

        # Verify error is captured
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]

    def test_verify_phone_number_valid(self):
        """Test phone number verification for valid number"""
        # Setup mock lookup response
        mock_lookup = MagicMock()
        mock_lookup.carrier = {"name": "Test Carrier", "type": "mobile"}
        mock_lookup.country_code = "US"
        mock_lookup.national_format = "(234) 567-8901"

        # Setup mock lookup method
        mock_phone_lookup = MagicMock()
        mock_phone_lookup.fetch.return_value = mock_lookup
        self.mock_twilio_client.lookups.phone_numbers.return_value = mock_phone_lookup

        # Call verify_phone_number
        result = self.client.verify_phone_number("+12345678901")

        # Verify result
        assert result["success"] is True
        assert result["valid"] is True
        assert "data" in result
        assert "carrier" in result["data"]
        assert "country_code" in result["data"]

    def test_get_message_status(self):
        """Test getting message status"""
        # Setup mock message
        mock_message = MagicMock()
        mock_message.sid = "SM12345"
        mock_message.status = "delivered"
        mock_message.to = "+12345678901"
        mock_message.from_ = "+19876543210"
        mock_message.body = "Test message"
        mock_message.date_sent = "2023-01-01T12:00:00Z"
        mock_message.error_code = None
        mock_message.error_message = None

        # Setup mock messages method
        mock_messages = MagicMock()
        mock_messages.fetch.return_value = mock_message
        self.mock_twilio_client.messages.return_value = mock_messages

        # Call get_message_status
        result = self.client.get_message_status("SM12345")

        # Verify result
        assert result["success"] is True
        assert result["status"] == "delivered"
        assert "data" in result
        assert result["data"]["sid"] == "SM12345"
        assert result["data"]["to"] == "+12345678901"

        # Verify Twilio API was called correctly
        self.mock_twilio_client.messages.assert_called_once_with("SM12345")
