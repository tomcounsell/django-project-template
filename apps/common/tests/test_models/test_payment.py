"""
Tests for the Payment model.
"""

import pytest
from django.test import TestCase
from django.utils import timezone

from apps.common.models import Payment, Subscription, User


class PaymentTestCase(TestCase):
    """Test case for the Payment model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        # Create a subscription
        self.subscription = Subscription.objects.create(
            stripe_id="sub_test123",
            stripe_customer_id="cus_test123",
            stripe_price_id="price_test123",
            status=Subscription.STATUS_ACTIVE,
            plan_name="Test Plan",
            user=self.user,
        )

        # Create a payment
        self.payment = Payment.objects.create(
            stripe_id="pi_test123",
            stripe_customer_id="cus_test123",
            amount=1999,  # $19.99
            currency="USD",
            status=Payment.STATUS_SUCCEEDED,
            payment_method=Payment.PAYMENT_METHOD_CARD,
            description="Monthly subscription payment",
            user=self.user,
            subscription=self.subscription,
        )

    def test_payment_creation(self):
        """Test that a payment can be created."""
        self.assertEqual(self.payment.stripe_id, "pi_test123")
        self.assertEqual(self.payment.status, Payment.STATUS_SUCCEEDED)
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.amount, 1999)
        self.assertEqual(self.payment.currency, "USD")

    def test_amount_display_property(self):
        """Test the amount_display property."""
        self.assertEqual(self.payment.amount_display, "$19.99 USD")

        # Test different amount and currency
        self.payment.amount = 500
        self.payment.currency = "EUR"
        self.payment.save()
        self.assertEqual(self.payment.amount_display, "$5.00 EUR")

    def test_is_successful_property(self):
        """Test the is_successful property."""
        # Successful payment
        self.assertTrue(self.payment.is_successful)

        # Failed payment
        self.payment.status = Payment.STATUS_FAILED
        self.payment.save()
        self.assertFalse(self.payment.is_successful)

        # Pending payment
        self.payment.status = Payment.STATUS_PENDING
        self.payment.save()
        self.assertFalse(self.payment.is_successful)

    def test_owner_display_property(self):
        """Test the owner_display property."""
        # User payment
        self.assertEqual(self.payment.owner_display, f"User: {self.user.email}")

        # No owner
        self.payment.user = None
        self.payment.save()
        self.assertEqual(self.payment.owner_display, "Unknown")

    def test_payment_type_display_property(self):
        """Test the payment_type_display property."""
        # Subscription payment
        self.assertEqual(
            self.payment.payment_type_display,
            f"Subscription: {self.subscription.plan_name}",
        )

        # One-time payment
        self.payment.subscription = None
        self.payment.save()
        self.assertEqual(self.payment.payment_type_display, "One-time payment")
