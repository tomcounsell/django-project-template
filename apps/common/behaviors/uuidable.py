from django.db import models
import uuid


class UUIDable(models.Model):
    """
    Adds a universally unique identifier (UUID) field to the model for global uniqueness and external integrations.

    Fields:
        uuid (UUIDField): Automatically generated UUID for the model instance.
    """

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True
