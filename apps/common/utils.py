
from django.core.exceptions import ValidationError
from django.db import models

#https://djangosnippets.org/snippets/1741/
class DollarField(models.IntegerField):
  description = "A field to save dollars as pennies(int) in db, but act like a float"
  __metaclass__ =  models.SubfieldBase

  def get_db_prep_value(self, value, *args, **kwargs):
    if value is None:
      return None
    return int(value * 100)

  def to_python(self, value):
    if value is None or isinstance(value, float):
      return value
    try:
      return float(value) / 100
    except (TypeError, ValueError):
      raise ValidationError("This value must be an integer or a string represents an integer.")

  def formfield(self, **kwargs):
    from django.forms import FloatField
    defaults = {'form_class': FloatField}
    defaults.update(kwargs)
    return super(DollarField, self).formfield(**defaults)

