# Test Conventions

This document outlines the testing approach, conventions, and best practices for the Django Project Template. Following these guidelines will ensure consistency across the codebase and maintain high test coverage.

## Core Testing Principles

1. **Test-Driven Development (TDD)**
   - Write tests BEFORE implementing features
   - Follow the Red-Green-Refactor cycle:
     1. Write a failing test (Red)
     2. Implement just enough code to pass the test (Green)
     3. Refactor while maintaining passing tests

2. **Coverage Goals**
   - Aim for 100% test coverage for:
     - Models
     - Behavior mixins
     - Utilities
   - Strive for 90%+ coverage for views and APIs
   - Use `.coveragerc` to exclude boilerplate code from coverage metrics

3. **Database Usage**
   - Always use PostgreSQL for tests, never SQLite
   - Tests should use transaction rollbacks for isolation and speed
   - Test fixtures should be minimal but sufficient

## Test Organization

### Directory Structure

```
apps/
  app_name/
    tests/
      __init__.py
      factories.py           # Model factories for this app
      test_forms/            # Form tests
        test_form_name.py
      test_models/           # Model tests
        test_model_name.py
      test_views/            # View tests
        test_view_name.py
      test_serializers/      # API serializer tests
        test_serializer.py
  common/
    behaviors/
      tests/
        test_behaviors.py    # Standalone behavior tests (Python 3.12 compatible)
    tests/
      factories.py           # Shared model factories
      test_behaviors/        # Django-based behavior mixin tests
        test_behavior_name.py
```

### Test Class Naming

- Test classes should be named with format: `{Subject}TestCase`
- Example: `UserModelTestCase`, `LoginViewTestCase`, `APIEndpointTestCase`

### Test Method Naming

- Test methods should follow the pattern: `test_{condition_being_tested}`
- Include the expected behavior and condition being tested
- Examples:
  - `test_user_creation_with_valid_data_succeeds`
  - `test_login_with_invalid_credentials_returns_error`
  - `test_api_returns_404_for_nonexistent_resource`

## Test Types and Their Implementation

### Model Tests

Model tests verify that your data models work correctly, including:

```python
# Example model test
from django.test import TestCase
from apps.common.models import Address

class AddressModelTestCase(TestCase):
    def setUp(self):
        self.address = Address.objects.create(
            line_1="123 Main St",
            city="New York",
            region="NY",
            postal_code="10001"
        )
    
    def test_string_representation(self):
        expected = "123 Main St New York, NY"
        self.assertEqual(str(self.address), expected)
        
    def test_property_returns_expected_value(self):
        self.assertEqual(self.address.formatted_address, "123 Main St, New York, NY 10001")
```

### Behavior Mixin Tests

There are two types of behavior mixin tests:

1. **Django-integrated tests** - Test mixins with Django models
2. **Standalone tests** - Test mixins using mocks (Python 3.12 compatible)

#### Django-Integrated Tests

```python
# Example behavior test with Django
from django.test import TestCase
from apps.common.behaviors.annotatable import Annotatable
from apps.common.models.note import Note

class AnnotatableModel(Annotatable):
    class Meta:
        app_label = 'test_app'

class AnnotatableTest(TestCase):
    def setUp(self):
        self.obj = AnnotatableModel.objects.create()
        self.note = Note.objects.create(text="Test note")
    
    def test_has_notes_property_returns_true_when_notes_exist(self):
        self.obj.notes.add(self.note)
        self.assertTrue(self.obj.has_notes)
```

#### Standalone Tests

```python
# Example standalone behavior test
import unittest
from unittest import mock
from datetime import datetime, timedelta

# Import behavior to test
from apps.common.behaviors.timestampable import Timestampable

class MockModel(Timestampable):
    pass

class TimestampableTest(unittest.TestCase):
    def test_was_created_today_returns_true_for_today(self):
        model = MockModel()
        model.created_at = datetime.now()
        self.assertTrue(model.was_created_today)
        
    def test_was_created_today_returns_false_for_yesterday(self):
        model = MockModel()
        model.created_at = datetime.now() - timedelta(days=1)
        self.assertFalse(model.was_created_today)

if __name__ == "__main__":
    unittest.main()
```

### View Tests

View tests verify that views render correctly and process form submissions appropriately:

```python
# Example view test
from django.test import TestCase
from django.urls import reverse
from apps.common.tests.factories import UserFactory

class HomeViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.login(username=self.user.username, password='password')
        self.url = reverse('home')
    
    def test_get_authenticated_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/home.html')
        
    def test_context_contains_expected_data(self):
        response = self.client.get(self.url)
        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'], self.user)
```

### API Tests

API tests verify that your API endpoints work correctly:

```python
# Example API test
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from apps.common.tests.factories import UserFactory

class UserAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('api:user-detail', kwargs={'pk': self.user.pk})
    
    def test_get_returns_expected_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user.username)
```

### Admin Tests

Admin tests verify that Django admin customizations work correctly:

```python
# Example admin test
import warnings
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

# Filter out timezone warnings during tests
warnings.filterwarnings(
    "ignore", 
    message="DateTimeField .* received a naive datetime", 
    category=RuntimeWarning
)

@override_settings(ALLOWED_HOSTS=['testserver'])
class AdminTestCase(TestCase):
    def setUp(self):
        # Use get_or_create to avoid duplicate user errors
        self.user, created = get_user_model().objects.get_or_create(
            username='admin_test',
            defaults={
                'email': 'admin_test@example.com',
                'is_superuser': True,
                'is_staff': True,
                'date_joined': timezone.now(),  # Use timezone-aware datetime
            }
        )
        
        if created:
            self.user.set_password('password123')
            self.user.save()
        
        self.client = Client()
        self.client.login(username='admin_test', password='password123')
    
    def test_admin_index(self):
        """Test the admin index page loads successfully."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Database')
    
    def test_custom_dashboard(self):
        """Test the custom admin dashboard."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        # Check for expected admin interface elements
        self.assertContains(response, 'ProjectName Database')
        self.assertContains(response, 'output.css')
```

## Test Factories

Use [factory_boy](https://factoryboy.readthedocs.io/) to create test objects:

```python
# Example factory
import factory
from django.contrib.auth import get_user_model
from apps.common.models import Team

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or "password"
        self.set_password(password)
        if create:
            self.save()

class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Team
    
    name = factory.Sequence(lambda n: f"Team {n}")
    created_by = factory.SubFactory(UserFactory)
```

## Running Tests

### Basic Test Commands

```bash
# Run all tests
DJANGO_SETTINGS_MODULE=settings pytest

# Run a specific test file
DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py

# Run a specific test class
DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py::AddressModelTestCase

# Run a specific test method
DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py::AddressModelTestCase::test_string_representation

# Run standalone behavior tests (Python 3.12 compatible)
python apps/common/behaviors/tests/test_behaviors.py
```

### Coverage Commands

```bash
# Run tests with coverage report
DJANGO_SETTINGS_MODULE=settings pytest --cov=apps

# Generate HTML coverage report
DJANGO_SETTINGS_MODULE=settings pytest --cov=apps --cov-report=html:apps/common/tests/coverage_html_report

# Generate XML coverage report (for CI)
DJANGO_SETTINGS_MODULE=settings pytest --cov=apps --cov-report=xml:apps/common/tests/coverage.xml
```

## Mocking

Use the `unittest.mock` library for mocking external dependencies:

```python
from unittest import mock
from django.test import TestCase
from apps.integration.services import EmailService

class EmailServiceTestCase(TestCase):
    @mock.patch('apps.integration.services.requests.post')
    def test_send_email_makes_expected_api_call(self, mock_post):
        # Setup mock
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'id': '123'}
        
        # Call the method
        service = EmailService()
        result = service.send_email('user@example.com', 'Subject', 'Body')
        
        # Assertions
        self.assertTrue(result)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['to'], 'user@example.com')
```

## Common Pitfalls

1. **Database Leakage**: Ensure tests clean up after themselves to avoid test interdependence
2. **Slow Tests**: Minimize database calls; use setUpTestData for class-level fixtures
3. **Brittle Tests**: Don't test implementation details, test outcomes and behavior
4. **Insufficient Coverage**: Ensure all edge cases are covered
5. **Overlooking Permissions**: For views and API endpoints, test different permission scenarios
6. **Timezone Issues**: Be explicit about datetime comparisons and aware of timezone settings
   - Use timezone.now() instead of naive datetime objects
   - Consider using filter_warnings in pyproject.toml for persistent warnings

## Best Practices

1. **Use Descriptive Assertions**: Prefer `assertEqual` over `assertTrue(a == b)` for better error messages
2. **Test Invalid Cases**: Test what should fail, not just what should succeed
3. **Keep Tests Independent**: Tests should not depend on each other
4. **Use Fixtures Wisely**: Keep fixtures minimal and focused
5. **Test Edge Cases**: Consider boundary values and special cases
6. **Follow AAA Pattern**: Arrange, Act, Assert - keep these sections clear and separate
7. **Parameterize Similar Tests**: Use `pytest.mark.parametrize` for testing multiple similar cases

By following these testing conventions, you'll ensure maintainable, reliable tests that provide confidence in the codebase.