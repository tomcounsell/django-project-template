"""
Tests for Stripe webhook views.
"""
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class StripeWebhookTestCase(TestCase):
    """Test cases for the Stripe webhook endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.webhook_url = reverse('api:stripe-webhook')
        # Mock payload for testing
        self.payload = json.dumps({
            "id": "evt_test123",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test123",
                    "customer": "cus_test123",
                    "customer_email": "test@example.com"
                }
            }
        }).encode('utf-8')
        self.signature = "test_signature"
        
    @patch('apps.api.views.stripe.handle_stripe_webhook')
    def test_webhook_success(self, mock_handle_webhook):
        """Test successful webhook processing."""
        # Mock successful response
        mock_handle_webhook.return_value = {
            "success": True,
            "status": "processed",
            "event_type": "checkout.session.completed"
        }
        
        # Send request
        response = self.client.post(
            self.webhook_url,
            self.payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=self.signature
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["status"], "processed")
        self.assertEqual(response.data["event_type"], "checkout.session.completed")
        
        # Verify webhook handler was called correctly
        mock_handle_webhook.assert_called_once_with(self.payload, self.signature)
    
    @patch('apps.api.views.stripe.handle_stripe_webhook')
    def test_webhook_failure(self, mock_handle_webhook):
        """Test webhook processing failure."""
        # Mock failure response
        mock_handle_webhook.return_value = {
            "success": False,
            "error": "Invalid signature",
            "status": "invalid_signature"
        }
        
        # Send request
        response = self.client.post(
            self.webhook_url,
            self.payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=self.signature
        )
        
        # Check response - should still be 200 to prevent Stripe from retrying
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"], "Invalid signature")
        
    def test_webhook_missing_signature(self):
        """Test webhook with missing signature header."""
        # Send request without signature header
        response = self.client.post(
            self.webhook_url,
            self.payload,
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "No Stripe signature header")
    
    @patch('apps.api.views.stripe.handle_stripe_webhook')
    def test_webhook_unexpected_error(self, mock_handle_webhook):
        """Test webhook with unexpected error."""
        # Mock unexpected error
        mock_handle_webhook.side_effect = Exception("Unexpected error")
        
        # Send request
        response = self.client.post(
            self.webhook_url,
            self.payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=self.signature
        )
        
        # Check response - should still be 200 to prevent Stripe from retrying
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"], "Internal server error")