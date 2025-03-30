"""
Base class for behavior tests.

This file is kept for backwards compatibility. In the current structure,
behavior tests are organized into:

1. test_behaviors/ - A package containing Django TestCase-based tests
2. test_behaviors_direct.py - A module with standalone unittest-based tests

See the behavior_test_guide.md for more information on the test structure.
"""

class BehaviorTestCaseMixin(object):
    """
    Base mixin for behavior tests.
    
    This class is maintained for backwards compatibility.
    New tests should use test_behaviors/test_mixins.py instead.
    """
    def get_model(self):
        """Return the model class for testing"""
        return getattr(self, 'model')
  
    def create_instance(self, **kwargs):
        """Create a model instance with the given kwargs"""
        raise NotImplementedError("Implement me")