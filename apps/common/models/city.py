import uuid
from django.db import models


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, blank=True)
    code = models.CharField(
        max_length=3, unique=True, blank=True
    )  # typically the airport code

    # assuming cities stick to one country nationwide
    country = models.ForeignKey(
        "common.Country", related_name="cities", null=False, on_delete=models.PROTECT
    )

    # MODEL PROPERTIES
    @property
    def currency(self):
        return self.country.currency

    # MODEL FUNCTIONS
    def __str__(self):
        return f"{self.name}, {self.country.name} ({self.code})"

    class Meta:
        verbose_name_plural = "cities"


from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=City)
def lowercase_code(sender, instance, **kwargs):
    instance.code = instance.code.lower()
