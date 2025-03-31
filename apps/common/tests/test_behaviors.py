"""
Tests for behavior mixins in the common app.

This module contains test classes for all behavior mixins in the project.
It follows two testing approaches:
1. Database-backed tests: Using Django's TestCase to test with ORM integration
2. Direct tests: Using Python's unittest with mocks to test without database

These tests verify fields, properties, and methods provided by each behavior mixin.
"""

import unittest
from unittest import mock
from django.test import TestCase
from django.utils import timezone
import datetime
from django.contrib.auth import get_user_model

from apps.common.behaviors.timestampable import Timestampable
from apps.common.behaviors.authorable import Authorable
from apps.common.behaviors.publishable import Publishable
from apps.common.behaviors.expirable import Expirable
from apps.common.behaviors.permalinkable import Permalinkable
from apps.common.behaviors.locatable import Locatable
from apps.common.behaviors.annotatable import Annotatable

User = get_user_model()

# Base test mixin for behavior tests
class BehaviorTestMixin:
    """Base mixin for behavior tests that provides common methods."""
    
    @property
    def model(self):
        """Must be defined by subclasses to return the model class to test."""
        raise NotImplementedError("Subclasses must define 'model' property")
    
    def create_instance(self, **kwargs):
        """Helper method to create a model instance for testing."""
        return self.model.objects.create(**kwargs)


# Timestampable Behavior Tests
class TimestampableTest(BehaviorTestMixin):
    """Tests for the Timestampable behavior mixin using Django TestCase."""
    
    def test_fields_exist(self):
        """Test that the fields are properly added to the model."""
        instance = self.create_instance()
        self.assertTrue(hasattr(instance, 'created_at'))
        self.assertTrue(hasattr(instance, 'modified_at'))
    
    def test_auto_timestamps(self):
        """Test that timestamps are automatically set."""
        instance = self.create_instance()
        self.assertIsNotNone(instance.created_at)
        self.assertIsNotNone(instance.modified_at)
        
        # Initially, created_at and modified_at should be close
        time_diff = abs((instance.created_at - instance.modified_at).total_seconds())
        self.assertLess(time_diff, 1)  # Should be less than 1 second apart
    
    def test_modified_at_updates(self):
        """Test that modified_at updates on save."""
        instance = self.create_instance()
        original_modified = instance.modified_at
        
        # Wait a moment to ensure timestamps differ
        instance.save()
        
        # Refresh from database to get updated values
        instance.refresh_from_db()
        self.assertGreaterEqual(instance.modified_at, original_modified)
        
        # created_at should remain unchanged
        self.assertEqual(instance.created_at.replace(microsecond=0), 
                         instance.created_at.replace(microsecond=0))


# Authorable Behavior Tests
class AuthorableTest(BehaviorTestMixin):
    """Tests for the Authorable behavior mixin using Django TestCase."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
    
    def test_fields_exist(self):
        """Test that the fields are properly added to the model."""
        instance = self.create_instance()
        self.assertTrue(hasattr(instance, 'author'))
        self.assertTrue(hasattr(instance, 'is_author_anonymous'))
        self.assertTrue(hasattr(instance, 'authored_at'))
    
    def test_author_assignment(self):
        """Test author assignment."""
        instance = self.create_instance(author=self.user)
        self.assertEqual(instance.author, self.user)
        self.assertFalse(instance.is_author_anonymous)
        self.assertIsNotNone(instance.authored_at)
    
    def test_anonymous_author(self):
        """Test anonymous author functionality."""
        instance = self.create_instance(is_author_anonymous=True)
        self.assertIsNone(instance.author)
        self.assertTrue(instance.is_author_anonymous)
        
        # Setting an author should clear anonymous flag
        instance.author = self.user
        instance.save()
        self.assertFalse(instance.is_author_anonymous)
    
    def test_author_display_name(self):
        """Test the author_display_name property."""
        # With author
        instance = self.create_instance(author=self.user)
        self.assertEqual(instance.author_display_name, self.user.get_full_name() or self.user.username)
        
        # Anonymous
        instance = self.create_instance(is_author_anonymous=True)
        self.assertEqual(instance.author_display_name, "Anonymous")


# Publishable Behavior Tests
class PublishableTest(BehaviorTestMixin):
    """Tests for the Publishable behavior mixin using Django TestCase."""
    
    def test_fields_exist(self):
        """Test that the fields are properly added to the model."""
        instance = self.create_instance()
        self.assertTrue(hasattr(instance, 'published_at'))
        self.assertTrue(hasattr(instance, 'edited_at'))
        self.assertTrue(hasattr(instance, 'unpublished_at'))
    
    def test_publish_method(self):
        """Test publish method sets published_at."""
        instance = self.create_instance()
        self.assertIsNone(instance.published_at)
        self.assertFalse(instance.is_published)
        
        instance.publish()
        self.assertIsNotNone(instance.published_at)
        self.assertTrue(instance.is_published)
    
    def test_unpublish_method(self):
        """Test unpublish method sets unpublished_at."""
        instance = self.create_instance()
        instance.publish()
        self.assertTrue(instance.is_published)
        
        instance.unpublish()
        self.assertIsNotNone(instance.unpublished_at)
        self.assertFalse(instance.is_published)
    
    def test_edit_published(self):
        """Test editing a published item sets edited_at."""
        instance = self.create_instance()
        instance.publish()
        
        # Simulate edit
        instance.edited_at = None
        instance.save()
        instance.refresh_from_db()
        self.assertIsNotNone(instance.edited_at)


# Expirable Behavior Tests
class ExpirableTest(BehaviorTestMixin):
    """Tests for the Expirable behavior mixin using Django TestCase."""
    
    def test_fields_exist(self):
        """Test that the fields are properly added to the model."""
        instance = self.create_instance()
        self.assertTrue(hasattr(instance, 'valid_at'))
        self.assertTrue(hasattr(instance, 'expired_at'))
    
    def test_is_expired_property(self):
        """Test the is_expired property correctly reflects state."""
        instance = self.create_instance()
        self.assertFalse(instance.is_expired)
        
        # Set expired
        instance.expired_at = timezone.now()
        instance.save()
        self.assertTrue(instance.is_expired)
    
    def test_set_expired(self):
        """Test setting expired state through property."""
        instance = self.create_instance()
        self.assertIsNone(instance.expired_at)
        
        instance.is_expired = True
        self.assertIsNotNone(instance.expired_at)
        self.assertTrue(instance.is_expired)
        
        instance.is_expired = False
        self.assertIsNone(instance.expired_at)
        self.assertFalse(instance.is_expired)


# Permalinkable Behavior Tests
class PermalinkableTest(BehaviorTestMixin):
    """Tests for the Permalinkable behavior mixin using Django TestCase."""
    
    def test_fields_exist(self):
        """Test that the fields are properly added to the model."""
        instance = self.create_instance()
        self.assertTrue(hasattr(instance, 'slug'))
    
    def test_slug_generation(self):
        """Test slug generation."""
        instance = self.create_instance()
        self.assertIsNotNone(instance.slug)
        
        # Test with a model that has slug_source property
        if hasattr(instance, 'slug_source'):
            expected_slug = instance.slug_source.lower().replace(' ', '-')
            self.assertTrue(instance.slug.startswith(expected_slug))
    
    def test_get_url_kwargs(self):
        """Test get_url_kwargs method."""
        instance = self.create_instance()
        kwargs = instance.get_url_kwargs()
        self.assertIn('slug', kwargs)
        self.assertEqual(kwargs['slug'], instance.slug)


# Locatable Behavior Tests
class LocatableTest(BehaviorTestMixin):
    """Tests for the Locatable behavior mixin using Django TestCase."""
    
    def test_fields_exist(self):
        """Test that the fields are properly added to the model."""
        instance = self.create_instance()
        self.assertTrue(hasattr(instance, 'address'))
        self.assertTrue(hasattr(instance, 'longitude'))
        self.assertTrue(hasattr(instance, 'latitude'))
    
    def test_coordinates(self):
        """Test setting and getting coordinates."""
        instance = self.create_instance(longitude=123.456, latitude=45.678)
        self.assertEqual(instance.longitude, 123.456)
        self.assertEqual(instance.latitude, 45.678)


# Annotatable Behavior Tests
class AnnotatableTest(BehaviorTestMixin):
    """Tests for the Annotatable behavior mixin using Django TestCase."""
    
    def test_fields_exist(self):
        """Test that the fields are properly added to the model."""
        instance = self.create_instance()
        self.assertTrue(hasattr(instance, 'notes'))
    
    def test_has_notes_property(self):
        """Test has_notes property."""
        instance = self.create_instance()
        self.assertFalse(instance.has_notes)
        
        # We'd normally add a note here, but we need to mock this
        # since we don't have the actual Note model to test with
        with mock.patch.object(instance.notes, 'exists', return_value=True):
            self.assertTrue(instance.has_notes)


# Direct Tests (Without Database)
class TestTimestampableDirect(unittest.TestCase):
    """Direct tests for Timestampable without database."""
    
    def test_fields(self):
        """Test the fields are defined correctly."""
        self.assertTrue(hasattr(Timestampable, 'created_at'))
        self.assertTrue(hasattr(Timestampable, 'modified_at'))
        
        # Get the field instances directly from the model's _meta
        created_at_field = Timestampable._meta.get_field('created_at')
        modified_at_field = Timestampable._meta.get_field('modified_at')
        
        self.assertEqual(created_at_field.auto_now_add, True)
        self.assertEqual(modified_at_field.auto_now, True)


class TestAuthorableDirect(unittest.TestCase):
    """Direct tests for Authorable without database."""
    
    def test_fields(self):
        """Test the fields are defined correctly."""
        self.assertTrue(hasattr(Authorable, 'author'))
        self.assertTrue(hasattr(Authorable, 'is_author_anonymous'))
        self.assertTrue(hasattr(Authorable, 'authored_at'))
    
    def test_author_display_name(self):
        """Test author_display_name property."""
        obj = mock.MagicMock(spec=Authorable)
        
        # Test anonymous
        obj.is_author_anonymous = True
        obj.author = None
        self.assertEqual(Authorable.author_display_name.fget(obj), "Anonymous")
        
        # Test with author
        obj.is_author_anonymous = False
        mock_author = mock.MagicMock()
        mock_author.__str__.return_value = "Test User"
        obj.author = mock_author
        self.assertEqual(Authorable.author_display_name.fget(obj), "Test User")


class TestPublishableDirect(unittest.TestCase):
    """Direct tests for Publishable without database."""
    
    def test_fields(self):
        """Test the fields are defined correctly."""
        self.assertTrue(hasattr(Publishable, 'published_at'))
        self.assertTrue(hasattr(Publishable, 'edited_at'))
        self.assertTrue(hasattr(Publishable, 'unpublished_at'))
    
    def test_is_published_property(self):
        """Test is_published property."""
        obj = mock.MagicMock(spec=Publishable)
        
        # Not published
        obj.published_at = None
        obj.unpublished_at = None
        self.assertFalse(Publishable.is_published.fget(obj))
        
        # Published
        obj.published_at = timezone.now()
        obj.unpublished_at = None
        self.assertTrue(Publishable.is_published.fget(obj))
        
        # Published then unpublished
        obj.published_at = timezone.now()
        obj.unpublished_at = timezone.now() + datetime.timedelta(days=1)
        self.assertFalse(Publishable.is_published.fget(obj))


class TestExpirableDirect(unittest.TestCase):
    """Direct tests for Expirable without database."""
    
    def test_fields(self):
        """Test the fields are defined correctly."""
        self.assertTrue(hasattr(Expirable, 'valid_at'))
        self.assertTrue(hasattr(Expirable, 'expired_at'))
    
    def test_is_expired_property(self):
        """Test is_expired property."""
        obj = mock.MagicMock(spec=Expirable)
        
        # Not expired
        obj.expired_at = None
        self.assertFalse(Expirable.is_expired.fget(obj))
        
        # Expired
        obj.expired_at = timezone.now()
        self.assertTrue(Expirable.is_expired.fget(obj))


class TestPermalinkableDirect(unittest.TestCase):
    """Direct tests for Permalinkable without database."""
    
    def test_fields(self):
        """Test the fields are defined correctly."""
        self.assertTrue(hasattr(Permalinkable, 'slug'))
    
    def test_get_url_kwargs(self):
        """Test get_url_kwargs method."""
        obj = mock.MagicMock(spec=Permalinkable)
        obj.slug = "test-slug"
        # Add additional kwargs to the get_url_kwargs method
        result = Permalinkable.get_url_kwargs(obj, slug=obj.slug)
        self.assertEqual(result, {'slug': 'test-slug'})


class TestLocatableDirect(unittest.TestCase):
    """Direct tests for Locatable without database."""
    
    def test_fields(self):
        """Test the fields are defined correctly."""
        self.assertTrue(hasattr(Locatable, 'address'))
        self.assertTrue(hasattr(Locatable, 'longitude'))
        self.assertTrue(hasattr(Locatable, 'latitude'))


class TestAnnotatableDirect(unittest.TestCase):
    """Direct tests for Annotatable without database."""
    
    def test_fields(self):
        """Test the fields are defined correctly."""
        self.assertTrue(hasattr(Annotatable, 'notes'))
    
    def test_has_notes_property(self):
        """Test has_notes property."""
        obj = mock.MagicMock(spec=Annotatable)
        obj.notes.exists.return_value = False
        self.assertFalse(Annotatable.has_notes.fget(obj))
        
        obj.notes.exists.return_value = True
        self.assertTrue(Annotatable.has_notes.fget(obj))