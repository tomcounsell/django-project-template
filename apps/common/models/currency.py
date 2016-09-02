import uuid
from django.db import models
from apps.common.behaviors import Timestampable


class Currency(Timestampable, models.Model):
  id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name              = models.CharField(max_length=255)
  code              = models.CharField(max_length=3)

  # MODEL PROPERTIES

  # MODEL FUNCTIONS
  def __unicode__(self):
    return self.code
