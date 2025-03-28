from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.behaviors import Timestampable


class Payment(Timestampable, models.Model):
    """
    Model for storing payment information.
    """
    # User who made the payment
    user = models.ForeignKey(
        'common.User',
        related_name='payments',
        on_delete=models.CASCADE,
        help_text=_('User who made the payment')
    )
    
    # Subscription this payment is for (optional)
    subscription = models.ForeignKey(
        'common.Subscription',
        related_name='payments',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_('Subscription this payment is for')
    )
    
    # Stripe payment intent ID
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_('Stripe payment intent ID')
    )
    
    # Payment amount in cents
    amount = models.PositiveIntegerField(
        help_text=_('Payment amount in cents')
    )
    
    # Payment status
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('succeeded', _('Succeeded')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
        ('canceled', _('Canceled')),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('Payment status')
    )
    
    # Payment method used
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text=_('Payment method used (e.g., card, bank_transfer)')
    )
    
    # Last 4 digits of card (if card payment)
    last4 = models.CharField(
        max_length=4,
        blank=True,
        default="",
        help_text=_('Last 4 digits of card')
    )
    
    # Paid at datetime
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the payment was made')
    )
    
    # Refunded at datetime
    refunded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the payment was refunded')
    )
    
    # Description
    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_('Payment description')
    )
    
    # Receipt URL
    receipt_url = models.URLField(
        blank=True,
        default="",
        help_text=_('URL for payment receipt')
    )
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ('-created_at',)
    
    def __str__(self):
        return f"Payment {self.id} - {self.amount/100:.2f} ({self.status})"
    
    @property
    def amount_display(self):
        """
        Display the amount in dollars rather than cents.
        """
        return f"${self.amount/100:.2f}"
    
    @property
    def is_successful(self):
        """
        Check if the payment was successful.
        """
        return self.status == 'succeeded'