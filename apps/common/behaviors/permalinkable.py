from django.core.validators import validate_slug
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify


class Permalinkable(models.Model):
    slug = models.SlugField(
        null=True, blank=True, validators=[validate_slug], unique=True
    )

    class Meta:
        abstract = True

    def get_url_kwargs(self, **kwargs):
        kwargs.update(getattr(self, "url_kwargs", {}))
        return kwargs

    # @models.permalink
    # def get_absolute_url(self):
    #     url_kwargs = self.get_url_kwargs(slug=self.slug)
    #     return (self.url_name, (), url_kwargs)


@receiver(pre_save)
def pre_save_slug(sender, instance, *args, **kwargs):
    if hasattr(sender, 'mro') and Permalinkable in sender.mro():
        if not instance.slug and hasattr(instance, "slug_source"):
            instance.slug = slugify(instance.slug_source)
