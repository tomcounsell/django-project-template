from datetime import datetime, timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from apps.common.behaviors.publishable import Publishable
from .test_mixins import BehaviorTestCaseMixin


class PublishableModel(Publishable):
    class Meta:
        app_label = 'test_app'


class PublishableTest(BehaviorTestCaseMixin, TestCase):
    @property
    def model(self):
        return PublishableModel
    
    def test_is_published_false_by_default(self):
        # Test that a new object is not published by default
        obj = self.model.objects.create()
        self.assertFalse(obj.is_published)
    
    def test_is_published_true_when_published_in_past(self):
        # Test that an object with published_at in the past is published
        past_time = timezone.now() - timedelta(days=1)
        obj = self.model.objects.create(published_at=past_time)
        self.assertTrue(obj.is_published)
    
    def test_is_published_false_when_published_in_future(self):
        # Test that an object with published_at in the future is not published
        future_time = timezone.now() + timedelta(days=1)
        obj = self.model.objects.create(published_at=future_time)
        self.assertFalse(obj.is_published)
    
    def test_is_published_false_when_unpublished(self):
        # Test that an object that was published and then unpublished is not published
        past_time = timezone.now() - timedelta(days=2)
        unpublished_time = timezone.now() - timedelta(days=1)
        obj = self.model.objects.create(published_at=past_time, unpublished_at=unpublished_time)
        self.assertFalse(obj.is_published)
    
    def test_publish_method_updates_published_at(self):
        # Test that calling publish() sets published_at to now
        now = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            obj = self.model.objects.create()
            obj.publish()
            self.assertEqual(obj.published_at, now)
            self.assertTrue(obj.is_published)
    
    def test_unpublish_method_updates_unpublished_at(self):
        # Test that calling unpublish() sets unpublished_at to now
        now = timezone.now()
        past = now - timedelta(days=1)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            obj = self.model.objects.create(published_at=past)
            self.assertTrue(obj.is_published)
            obj.unpublish()
            self.assertEqual(obj.unpublished_at, now)
            self.assertFalse(obj.is_published)
    
    def test_setting_is_published_to_true_clears_unpublished_at(self):
        # Test that setting is_published = True clears unpublished_at
        now = timezone.now()
        past = now - timedelta(days=1)
        obj = self.model.objects.create(published_at=past, unpublished_at=past)
        self.assertFalse(obj.is_published)
        
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            obj.is_published = True
            self.assertIsNone(obj.unpublished_at)
            self.assertEqual(obj.published_at, now)
            self.assertTrue(obj.is_published)
    
    def test_setting_is_published_to_false_sets_unpublished_at(self):
        # Test that setting is_published = False sets unpublished_at
        now = timezone.now()
        past = now - timedelta(days=1)
        obj = self.model.objects.create(published_at=past)
        self.assertTrue(obj.is_published)
        
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            obj.is_published = False
            self.assertEqual(obj.unpublished_at, now)
            self.assertFalse(obj.is_published)