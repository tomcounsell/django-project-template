from unittest import mock

from django.test import TestCase
from django.db import models

from apps.common.behaviors.permalinkable import Permalinkable
from .test_mixins import BehaviorTestCaseMixin


class PermalinkableModel(Permalinkable):
    title = models.CharField(max_length=100)
    
    @property
    def slug_source(self):
        return self.title
    
    class Meta:
        app_label = 'test_app'


class PermalinkableTest(BehaviorTestCaseMixin, TestCase):
    @property
    def model(self):
        return PermalinkableModel

    def test_slug_generated_from_slug_source(self):
        # Test that slug is automatically generated from the slug_source property
        obj = self.model.objects.create(title="Test Title")
        obj.save()  # This should trigger the pre_save signal
        self.assertEqual(obj.slug, "test-title")
    
    def test_custom_slug_not_overridden(self):
        # Test that a custom slug is not overridden
        obj = self.model.objects.create(title="Test Title", slug="custom-slug")
        obj.save()
        self.assertEqual(obj.slug, "custom-slug")
    
    def test_get_url_kwargs(self):
        # Test the get_url_kwargs method
        obj = self.model.objects.create(title="Test Title")
        # Without url_kwargs attribute
        self.assertEqual(obj.get_url_kwargs(), {})
        
        # With additional kwargs
        kwargs = obj.get_url_kwargs(id=obj.id)
        self.assertEqual(kwargs, {'id': obj.id})
        
        # Set url_kwargs attribute and test
        obj.url_kwargs = {'test': 'value'}
        kwargs = obj.get_url_kwargs(id=obj.id)
        self.assertEqual(kwargs, {'id': obj.id, 'test': 'value'})
    
    def test_slug_with_special_characters(self):
        # Test slugify handles special characters correctly
        obj = self.model.objects.create(title="Test & Title with Spaces!")
        obj.save()
        self.assertEqual(obj.slug, "test-title-with-spaces")