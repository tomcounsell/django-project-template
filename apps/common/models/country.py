import uuid
from django.db import models


class Country(models.Model):  # could expand on pypi.python.org/pypi/django-countries
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, blank=True)
    code = models.CharField(
        max_length=3,
        unique=True,
        blank=True,
        help_text="ISO 3166-1 alpha-2 (eg. US, TH, GB)",
    )
    calling_code = models.CharField(
        max_length=3,
        blank=True,
        help_text="e.g. '1' for (+1 USA) or '66' (+66 TH)",
    )

    # assuming countries stick to one currency nationwide
    currency = models.ForeignKey(
        "common.Currency",
        related_name="countries",
        null=True,
        on_delete=models.SET_NULL,
    )

    # MODEL PROPERTIES

    # MODEL FUNCTIONS
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "countries"


from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Country)
def lowercase_code(sender, instance, **kwargs):
    instance.code = instance.code.lower()
