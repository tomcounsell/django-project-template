"""
Test utilities for behavior mixin tests.

This module provides base classes and helper methods for testing
behavior mixins with Django's TestCase.
"""

from django.db import models
from django.test import TestCase


class BehaviorTestCaseMixin(object):
    """
    Mixin for testing behavior mixins in models.
    
    This mixin provides a standard way to create model instances
    with behavior mixins for testing.
    
    Usage:
    1. Create a test class that inherits from both this mixin and TestCase
    2. Define a model property that returns a model class with the behavior
    3. Optionally override create_instance if you need custom instance creation
    
    Example:
    ```python
    class TimestampableTest(BehaviorTestCaseMixin, TestCase):
        @property
        def model(self):
            return TimestampableModel
            
        def test_property(self):
            obj = self.create_instance()
            self.assertTrue(obj.some_property)
    ```
    """
    @property
    def model(self):
        """Override this to return the model class to test"""
        raise NotImplementedError("Implement Me")

    def create_instance(self, **kwargs):
        """Create an instance of the model with the given kwargs"""
        return self.model.objects.create(**kwargs)
