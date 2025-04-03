from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.behaviors import Timestampable


class Payment(Timestampable, models.Model):
    """
    Model for storing payment information from various payment processors.

    This model tracks payments made by users, including details about the payment method,
    status, amount, and related subscription. It's designed to work with Stripe but
    could be extended to support other payment processors.

    Attributes:
        user (ForeignKey): The user who made the payment
        subscription (ForeignKey): Optional subscription this payment is for
        stripe_payment_intent_id (str): Stripe payment intent ID
        amount (int): Payment amount in cents
        status (str): Current payment status (pending, succeeded, failed, etc.)
        payment_method (str): Payment method used (e.g., card, bank_transfer)
        last4 (str): Last 4 digits of card (if card payment)
        paid_at (datetime): When the payment was made
        refunded_at (datetime): When the payment was refunded (if applicable)
        description (str): Payment description
        receipt_url (str): URL for payment receipt
        created_at (datetime): When this payment record was created (from Timestampable)
        modified_at (datetime): When this payment record was last modified (from Timestampable)

    Properties:
        amount_display (str): Formatted display of the amount in dollars
        is_successful (bool): Whether the payment was successful
    """

    # User who made the payment
    user = models.ForeignKey(
        "common.User",
        related_name="payments",
        on_delete=models.CASCADE,
        help_text=_("User who made the payment"),
    )

    # Subscription this payment is for (optional)
    subscription = models.ForeignKey(
        "common.Subscription",
        related_name="payments",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Subscription this payment is for"),
    )

    # Stripe payment intent ID
    stripe_payment_intent_id = models.CharField(
        max_length=255, blank=True, default="", help_text=_("Stripe payment intent ID")
    )

    # Payment amount in cents
    amount = models.PositiveIntegerField(help_text=_("Payment amount in cents"))

    # Payment status
    STATUS_CHOICES = (
        ("pending", _("Pending")),
        ("succeeded", _("Succeeded")),
        ("failed", _("Failed")),
        ("refunded", _("Refunded")),
        ("canceled", _("Canceled")),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text=_("Payment status"),
    )

    # Payment method used
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text=_("Payment method used (e.g., card, bank_transfer)"),
    )

    # Last 4 digits of card (if card payment)
    last4 = models.CharField(
        max_length=4, blank=True, default="", help_text=_("Last 4 digits of card")
    )

    # Paid at datetime
    paid_at = models.DateTimeField(
        null=True, blank=True, help_text=_("When the payment was made")
    )

    # Refunded at datetime
    refunded_at = models.DateTimeField(
        null=True, blank=True, help_text=_("When the payment was refunded")
    )

    # Description
    description = models.CharField(
        max_length=255, blank=True, default="", help_text=_("Payment description")
    )

    # Receipt URL
    receipt_url = models.URLField(
        blank=True, default="", help_text=_("URL for payment receipt")
    )

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """
        Get a string representation of the payment.

        Returns:
            str: A formatted string with payment ID, amount, and status
        """
        return f"Payment {self.id} - {self.amount/100:.2f} ({self.status})"

    @property
    def amount_display(self) -> str:
        """
        Display the amount in dollars rather than cents.

        Formats the amount stored in cents as a dollar amount with
        two decimal places and a dollar sign.

        Returns:
            str: Formatted dollar amount (e.g., "$19.99")
        """
        return f"${self.amount/100:.2f}"

    @property
    def is_successful(self) -> bool:
        """
        Check if the payment was successful.

        A payment is considered successful when its status is 'succeeded'.

        Returns:
            bool: True if the payment status is 'succeeded', False otherwise
        """
        return self.status == "succeeded"

    @property
    def is_refunded(self) -> bool:
        """
        Check if the payment was refunded.

        A payment is considered refunded when its status is 'refunded'.

        Returns:
            bool: True if the payment status is 'refunded', False otherwise
        """
        return self.status == "refunded"

    @property
    def card_display(self) -> str:
        """
        Get a display string for the card used, if available.

        Returns:
            str: Last 4 digits of the card with prefix, or empty string if not available
        """
        if self.payment_method == "card" and self.last4:
            return f"Card ending in {self.last4}"
        return ""
