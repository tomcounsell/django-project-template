from django.utils.translation import gettext_lazy as _
from datetime import datetime
import hashlib

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.common.behaviors import Timestampable


class User(AbstractUser, Timestampable):
    phone_number = models.CharField(max_length=15, default="", blank=True)

    # birthdate = models.DateField(null=True, blank=True)

    is_email_verified = models.BooleanField(default=False)
    is_beta_tester = models.BooleanField(default=False)
    agreed_to_terms_at = models.DateTimeField(null=True, blank=True)

    # Stripe integration
    stripe_customer_id = models.CharField(max_length=255, blank=True, default="")
    has_payment_method = models.BooleanField(default=False)

    # MODEL PROPERTIES
    @property
    def serialized(self):
        return {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_staff": self.is_staff,
            "is_active": self.is_active,
        }

    @property
    def four_digit_login_code(self):
        if self.email.endswith("@example.com"):
            return "1234"  # for test accounts
        hash_object = hashlib.md5(
            bytes(f"{self.id}{self.email}{self.last_login}", encoding="utf-8")
        )
        return str(int(hash_object.hexdigest(), 16))[-4:]

    @property
    def is_agreed_to_terms(self) -> bool:
        if self.agreed_to_terms_at and self.agreed_to_terms_at > timezone.make_aware(
            datetime(2019, 11, 1)
        ):
            return True
        return False

    @is_agreed_to_terms.setter
    def is_agreed_to_terms(self, value: bool):
        if value is True:
            self.agreed_to_terms_at = timezone.now()
        elif value is False and self.is_agreed_to_terms:
            self.agreed_to_terms_at = None
            
    @property
    def has_active_subscription(self) -> bool:
        """
        Check if the user has an active subscription.
        
        Returns:
            bool: True if the user has an active subscription, False otherwise
        """
        return hasattr(self, 'subscriptions') and self.subscriptions.filter(active=True).exists()

    @property
    def active_subscriptions(self):
        """
        Get the user's active subscriptions.
        
        Returns:
            QuerySet: The user's active subscriptions
        """
        if not hasattr(self, 'subscriptions'):
            return []
            
        return self.subscriptions.filter(status__in=['active', 'trialing'])
    
    @property
    def has_stripe_customer(self) -> bool:
        """
        Check if the user has a Stripe customer ID.
        
        Returns:
            bool: True if the user has a Stripe customer ID, False otherwise
        """
        return bool(self.stripe_customer_id)

    # MODEL FUNCTIONS
    def __str__(self):
        try:
            if self.first_name:
                return self.first_name + (
                    f" {self.last_name}" if self.last_name else ""
                )
            if self.username and "@" not in self.username:
                return self.username
            if self.is_email_verified:
                return self.email.split("@")[0]
            else:
                return f"{self.email} (unverified)"
        except:
            return f"User {self.id}"
            
    def get_active_subscription(self):
        """
        Get the user's active subscription.
        
        Returns:
            Subscription: The user's active subscription, or None if not found
        """
        if not hasattr(self, 'subscriptions'):
            return None
            
        return self.subscriptions.filter(status__in=['active', 'trialing']).first()
        
    def get_payment_history(self, limit=10):
        """
        Get the user's payment history.
        
        Args:
            limit: Maximum number of payments to return
            
        Returns:
            QuerySet: The user's payment history
        """
        if not hasattr(self, 'payments'):
            return []
            
        return self.payments.all()[:limit]
