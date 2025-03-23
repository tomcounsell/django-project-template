from datetime import datetime, timedelta
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from apps.common.behaviors.expirable import Expirable
from .test_mixins import BehaviorTestCaseMixin


class ExpirableModel(Expirable):
    class Meta:
        app_label = 'test_app'


class ExpirableTest(BehaviorTestCaseMixin, TestCase):
    @property
    def model(self):
        return ExpirableModel
    
    def test_is_expired_false_by_default(self):
        # Test that a new object is not expired by default
        obj = self.model.objects.create()
        self.assertFalse(obj.is_expired)
    
    def test_is_expired_true_when_expired_at_in_past(self):
        # Test that an object with expired_at in the past is expired
        past_time = timezone.now() - timedelta(days=1)
        obj = self.model.objects.create(expired_at=past_time)
        self.assertTrue(obj.is_expired)
    
    def test_is_expired_false_when_expired_at_in_future(self):
        # Test that an object with expired_at in the future is not expired
        future_time = timezone.now() + timedelta(days=1)
        obj = self.model.objects.create(expired_at=future_time)
        self.assertFalse(obj.is_expired)
    
    def test_set_is_expired_to_true_updates_expired_at(self):
        # Test that setting is_expired = True sets expired_at to now
        now = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            obj = self.model.objects.create()
            obj.is_expired = True
            self.assertEqual(obj.expired_at, now)
            self.assertTrue(obj.is_expired)
    
    def test_set_is_expired_to_false_clears_expired_at(self):
        # Test that setting is_expired = False clears expired_at if it was expired
        now = timezone.now()
        past = now - timedelta(days=1)
        obj = self.model.objects.create(expired_at=past)
        self.assertTrue(obj.is_expired)
        
        obj.is_expired = False
        self.assertIsNone(obj.expired_at)
        self.assertFalse(obj.is_expired)
    
    def test_set_is_expired_to_false_does_nothing_if_not_expired(self):
        # Test that setting is_expired = False does nothing if it wasn't expired
        obj = self.model.objects.create()
        self.assertFalse(obj.is_expired)
        self.assertIsNone(obj.expired_at)
        
        obj.is_expired = False
        self.assertIsNone(obj.expired_at)
        self.assertFalse(obj.is_expired)