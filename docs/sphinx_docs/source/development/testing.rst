Testing
=======

The Django Project Template follows a comprehensive testing approach with pytest.

Running Tests
------------

To run the test suite:

.. code-block:: bash

    DJANGO_SETTINGS_MODULE=settings pytest

For running tests with coverage:

.. code-block:: bash

    DJANGO_SETTINGS_MODULE=settings pytest --cov=apps

For running a specific test:

.. code-block:: bash

    DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py::AddressModelTestCase -v

Test Structure
-------------

Tests are organized by app and type:

- Model tests: `apps/{app_name}/tests/test_models/`
- View tests: `apps/{app_name}/tests/test_views/`
- Behavior tests: `apps/common/tests/test_behaviors/`
- API tests: `apps/api/tests/`

Test Practices
-------------

1. **Use Test-Driven Development**: Write tests before implementing features
2. **Use Factories**: Create factories for model instances in `apps/common/tests/factories.py`
3. **Test Edge Cases**: Ensure tests cover validation errors and edge cases
4. **Keep Tests Isolated**: Each test should be independent of others
5. **Test for Regressions**: Add tests for bugs to prevent recurrence

Model Tests
----------

Model tests focus on:

- Field validation
- Method behavior
- Constraint enforcement
- Relationship behavior

View Tests
---------

View tests focus on:

- Response status codes
- Template rendering
- Form handling
- Authentication/authorization
- HTMX-specific behavior

API Tests
--------

API tests focus on:

- Endpoint behavior
- Serialization/deserialization
- Authentication
- Permissions
- Rate limiting

Behavior Mixin Tests
------------------

Behavior mixin tests focus on:

- Mixin functionality
- Field defaults
- Method behavior
- Integration with models
