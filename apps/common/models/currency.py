import uuid
from django.db import models
from apps.common.behaviors import Timestampable


class Currency(Timestampable, models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(
        max_length=3,
        unique=True,
        help_text="ISO 4217 currency code (eg. USD, THB, GBP)",
    )

    # MODEL PROPERTIES

    # MODEL FUNCTIONS
    def __str__(self):
        return str(self.code).upper()

    class Meta:
        verbose_name_plural = "currencies"


from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Currency)
def lowercase_code(sender, instance, **kwargs):
    instance.code = instance.code.lower()
