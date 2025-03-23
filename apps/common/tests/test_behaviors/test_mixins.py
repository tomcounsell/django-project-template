from django.db import models
from django.test import TestCase

class BehaviorTestCaseMixin(object):
    """
    Mixin for testing behavior mixins in models.
    
    To use this mixin:
    1. Create a test class that inherits from both this mixin and TestCase
    2. Define a model property that returns a model class with the behavior
    3. Optionally override create_instance if you need custom instance creation
    """
    @property
    def model(self):
        """Override this to return the model class to test"""
        raise NotImplementedError("Implement Me")

    def create_instance(self, **kwargs):
        """Create an instance of the model with the given kwargs"""
        return self.model.objects.create(**kwargs)
