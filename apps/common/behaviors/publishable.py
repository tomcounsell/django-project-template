from django.db import models


class Publishable(models.Model):

  published_at    = models.DateTimeField(null=True, blank=True)
  unpublished_at  = models.DateTimeField(null=True, blank=True)

  class Meta:
    abstract = True

  @property
  def is_published(self):
    from django.utils.timezone import now
    if self.published_at and self.published_at < now() \
        and not (self.unpublished_at and self.unpublished_at < now()):
      return True
    else:
      return False


from .tests import BehaviorTestCaseMixin

class PublishableTests(BehaviorTestCaseMixin):
  def test_published_blogpost(self):
    from django.utils import timezone
    obj = self.create_instance(publish_date=timezone.now())
    self.assertTrue(obj.is_published)
    self.assertIn(obj, self.model.objects.published())
