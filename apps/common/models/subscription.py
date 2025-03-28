from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.common.behaviors import Timestampable


class Subscription(Timestampable, models.Model):
    """
    Model for storing subscription information.
    """
    # User who owns the subscription
    user = models.ForeignKey(
        'common.User',
        related_name='subscriptions',
        on_delete=models.CASCADE,
        help_text=_('User who owns the subscription')
    )
    
    # Stripe subscription ID
    stripe_subscription_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_('Stripe subscription ID')
    )
    
    # Subscription plan name
    plan_name = models.CharField(
        max_length=100,
        help_text=_('Subscription plan name')
    )
    
    # Subscription price in cents
    price = models.PositiveIntegerField(
        help_text=_('Subscription price in cents')
    )
    
    # Billing interval
    INTERVAL_CHOICES = (
        ('monthly', _('Monthly')),
        ('yearly', _('Yearly')),
        ('weekly', _('Weekly')),
        ('daily', _('Daily')),
    )
    interval = models.CharField(
        max_length=20,
        choices=INTERVAL_CHOICES,
        default='monthly',
        help_text=_('Billing interval')
    )
    
    # Subscription status
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('canceled', _('Canceled')),
        ('past_due', _('Past Due')),
        ('trialing', _('Trialing')),
        ('unpaid', _('Unpaid')),
        ('incomplete', _('Incomplete')),
        ('incomplete_expired', _('Incomplete Expired')),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text=_('Subscription status')
    )
    
    # Start date
    start_date = models.DateTimeField(
        default=timezone.now,
        help_text=_('When the subscription started')
    )
    
    # End date (null for active subscriptions)
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the subscription ended or will end')
    )
    
    # Canceled at datetime
    canceled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the subscription was canceled')
    )
    
    # Trial end date
    trial_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the trial period ends')
    )
    
    # Current period start
    current_period_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Start of the current billing period')
    )
    
    # Current period end
    current_period_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('End of the current billing period')
    )
    
    # Cancel at period end
    cancel_at_period_end = models.BooleanField(
        default=False,
        help_text=_('Whether the subscription will be canceled at the end of the current period')
    )
    
    class Meta:
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')
        ordering = ('-created_at',)
    
    def __str__(self):
        return f"{self.user} - {self.plan_name} ({self.status})"
    
    @property
    def is_active(self):
        """
        Check if the subscription is active.
        """
        return self.status in ['active', 'trialing']
    
    @property
    def is_trial(self):
        """
        Check if the subscription is in trial period.
        """
        return self.status == 'trialing'
    
    @property
    def price_display(self):
        """
        Display the price in dollars rather than cents.
        """
        return f"${self.price/100:.2f}/{self.interval}"
    
    @property
    def days_until_expiration(self):
        """
        Calculate days until the subscription expires.
        """
        if not self.end_date:
            return None
        
        delta = self.end_date - timezone.now()
        return max(0, delta.days)
    
    @property
    def is_expiring_soon(self):
        """
        Check if the subscription is expiring within 7 days.
        """
        days = self.days_until_expiration
        return days is not None and days <= 7 and self.is_active