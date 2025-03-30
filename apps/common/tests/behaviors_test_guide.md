# Behavior Mixins Testing Guide

This document explains the organization and usage of behavior mixin tests in the Django Project Template.

## Testing Approaches

There are two complementary approaches for testing behavior mixins:

1. **Django TestCase-based Tests** (`test_behaviors/`)
   - Located in `apps/common/tests/test_behaviors/`
   - Use Django's TestCase and a real database
   - Test behavior mixins integrated with Django's ORM
   - Primary testing method for most development

2. **Direct, Standalone Tests** (`test_behaviors_direct.py`)
   - Located at `apps/common/tests/test_behaviors_direct.py`
   - Use Python's unittest with mocks (no database)
   - Compatible with Python 3.12 without Django dependencies
   - Used for validating behavior mixins in isolation

## Running Tests

### Django TestCase-based Tests

Run all behavior tests with Django integration:

```bash
DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_behaviors/
```

Run a specific behavior test:

```bash
DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_behaviors/test_timestampable.py
```

### Direct, Standalone Tests

Run standalone tests without Django database:

```bash
python apps/common/tests/test_behaviors_direct.py
```

Or run specific test classes:

```bash
python -m unittest apps.common.tests.test_behaviors_direct.TestTimestampable
```

## Writing New Tests

### Django TestCase-based Tests

1. Create a new file in `test_behaviors/` directory, named after the behavior (e.g., `test_newbehavior.py`)
2. Inherit from `BehaviorTestCaseMixin` and `TestCase`
3. Create a simple model class implementing the behavior
4. Implement tests for all behavior methods and properties

Example:

```python
from django.test import TestCase
from apps.common.behaviors.newbehavior import NewBehavior
from .test_mixins import BehaviorTestCaseMixin

class NewBehaviorModel(NewBehavior):
    class Meta:
        app_label = 'test_app'

class NewBehaviorTest(BehaviorTestCaseMixin, TestCase):
    @property
    def model(self):
        return NewBehaviorModel
        
    def test_behavior_property(self):
        obj = self.create_instance()
        self.assertTrue(obj.has_expected_property)
```

### Direct, Standalone Tests

1. Add a new test class to `test_behaviors_direct.py`
2. Use mocks to simulate Django model behavior
3. Implement tests for all behavior methods and properties

Example:

```python
class TestNewBehavior(unittest.TestCase):
    def setUp(self):
        # Create a mock model instance
        self.obj = mock.MagicMock(spec=NewBehavior)
        
    def test_behavior_property(self):
        # Mock property setup
        type(self.obj).some_property = mock.PropertyMock(return_value="value")
        
        # Call the property
        result = NewBehavior.expected_property.fget(self.obj)
        
        # Assert expected result
        self.assertEqual(result, "expected")
```

## Which Approach to Use?

- **Use both** for comprehensive test coverage
- Django TestCase tests are better for integration testing
- Standalone tests are better for pure unit testing and Python 3.12 compatibility
- When adding a new behavior, implement both test types

## Test Organization

- Keep all behavior-specific tests within their respective files
- Ensure test names clearly describe the expected behavior
- Follow the pattern of "test_[method/property]_[expectation]"
- Add new behavior tests to `__init__.py` to enable proper test discovery