from django.db import models
from django.utils import timezone


class Publishable(models.Model):
    published_at = models.DateTimeField(null=True, blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    unpublished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def is_published(self):
        now = timezone.now()
        # If unpublished_at is more recent than published_at, the item is unpublished
        if self.unpublished_at and (not self.published_at or self.unpublished_at > self.published_at):
            return False
        # Item is published if it has a published_at date in the past
        elif self.published_at and self.published_at < now:
            return True
        else:
            return False

    @is_published.setter
    def is_published(self, value):
        if value and not self.is_published:
            self.unpublished_at = None
            self.published_at = timezone.now()
        elif not value and self.is_published:
            self.unpublished_at = timezone.now()

    def publish(self):
        self.is_published = True

    def unpublish(self):
        self.is_published = False
