from django.db import models
from django.utils import timezone

from apps.common.behaviors import timestampable


class SMS(timestampable.Timestampable, models.Model):
    """
    SMS model for storing text messages and their metadata.
    Used for sending SMS, tracking delivery status, and logging.
    """
    to_number = models.CharField(max_length=15)
    from_number = models.CharField(max_length=15, null=True, blank=True)
    body = models.TextField(default="")

    # Tracking fields
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "SMS"
        verbose_name_plural = "SMS Messages"

    def __str__(self):
        """String representation of the SMS."""
        return f"SMS to {self.to_number}: {self.body}"

    def mark_as_sent(self):
        """Marks the SMS as having been sent."""
        self.sent_at = timezone.now()
        self.save(update_fields=['sent_at'])

    def mark_as_read(self):
        """Marks the SMS as having been read by the recipient."""
        self.read_at = timezone.now()
        self.save(update_fields=['read_at'])

    def send(self):
        """
        Sends the SMS via SMS service integration.
        
        Note: This is a placeholder method. In a real implementation,
        this would integrate with a SMS service provider like Twilio.
        """
        # Implementation would go here
        self.mark_as_sent()
        return True