# End-to-End Testing with Browser-Use

This document describes how to perform end-to-end (E2E) testing for the Django Project Template using the browser-use library. E2E tests simulate real user interactions with the application through a browser.

> ⚠️ **Note**: This document is based on practical implementations found in:
> - `apps/public/tests/test_admin_e2e.py`: Testing admin login/logout workflows
> - `apps/public/tests/test_account_settings_e2e.py`: Testing user account settings functionality
> - `apps/public/tests/test_todo_workflow.py`: Testing Todo item creation and completion
> - `apps/public/tests/test_todo_visual.py`: Visual testing of the Todo workflow
> 
> Each example demonstrates both standard Django tests and browser-based tests using similar patterns.

## Overview

The Django Project Template supports E2E testing through a custom implementation built on:

1. **browser-use**: A Python library that enables AI-powered browser automation
2. **Playwright**: The underlying browser automation framework
3. **pytest-asyncio**: For running async tests with pytest

All E2E tests are isolated to local development environments and are not intended to run in CI pipelines, as they require a live server.

## Installation

To set up the E2E testing environment:

```bash
# Make sure you're in your virtual environment
source venv/bin/activate

# Install required packages
uv add --dev browser-use playwright pytest-asyncio

# Install playwright browser drivers
playwright install
```

Note: browser-use requires Python 3.11 or higher, which is compatible with your Python 3.12 environment.

## Running E2E Tests

### Standard Django Tests

Standard Django tests using `TestCase` and the Django test client run like any other Django tests:

```bash
# Run all account settings tests
DJANGO_SETTINGS_MODULE=settings pytest apps/public/tests/test_account_settings_e2e.py::AccountSettingsTestCase -v

# Run a specific test method
DJANGO_SETTINGS_MODULE=settings pytest apps/public/tests/test_account_settings_e2e.py::AccountSettingsTestCase::test_update_profile_info -v
```

These tests don't require a running server and provide fast, reliable feedback.

### Browser-Based Tests

Browser-based tests require a running Django server and the necessary dependencies installed:

```bash
# Terminal 1: Run the Django server
python manage.py runserver

# Terminal 2: Run the browser tests
DJANGO_SETTINGS_MODULE=settings pytest apps/public/tests/test_account_settings_e2e.py::AccountSettingsBrowserTestCase -v
```

If dependencies aren't installed or the server isn't running, these tests will be automatically skipped with an informative message.

### Running All Tests Together

You can run both standard and browser tests together:

```bash
# Run all tests in a file, with browser tests skipped if necessary
DJANGO_SETTINGS_MODULE=settings pytest apps/public/tests/test_account_settings_e2e.py -v
```

## Test Structure

### Configuration

The `EndToEndTestConfig` class in `test_e2e_patterns.py` controls test execution parameters:

```python
class EndToEndTestConfig:
    # Test server URL
    server_url: str = "http://localhost:8000"
    
    # Browser options
    headless: bool = True  # Set to False to see the browser during tests
    slow_mo: int = 0       # Add delay between actions (ms)
    browser_type: str = 'chromium'
    
    # Viewport settings
    viewport_width: int = 1280
    viewport_height: int = 720
    
    # Wait times
    default_timeout: int = 5000
    navigation_timeout: int = 10000
    
    # Screenshots directory
    screenshots_dir: str = 'test_screenshots'
```

### Base Test Class

All E2E tests extend `E2ETestBase`, which provides common functionality:

- Browser fixtures and setup
- Navigation helpers
- User authentication
- Screenshot capture
- Element assertions
- HTMX interaction utilities

### Test Categories

The template includes example test classes for different aspects of the application:

1. **`TestLoginForm`**: Tests basic form submission and authentication
2. **`TestHTMXInteractions`**: Tests HTMX components and dynamic updates
3. **`TestResponsiveLayout`**: Tests responsive design at different screen sizes
4. **`TestBrowserAgentAutomation`**: Tests complex user flows using AI-powered automation

## Writing E2E Tests

### Basic Test Structure

```python
@browser_test  # Skip if browser-use is not available
@pytest.mark.asyncio  # Mark as async test
class TestExample(E2ETestBase):
    """Test example functionality."""
    
    async def test_example_feature(self, browser_page):
        """Test specific feature."""
        page = browser_page
        
        # Navigate to a page
        await page.goto(f"{self.config.server_url}/example/")
        
        # Check element visibility
        assert await self.assert_element_visible(page, '.element-selector')
        
        # Interact with the page
        await page.fill('input[name="field"]', 'value')
        await page.click('button[type="submit"]')
        
        # Wait for response/navigation
        await page.wait_for_load_state('networkidle')
        
        # Verify results
        assert await self.assert_element_contains_text(page, '.result', 'Expected text')
```

### Testing HTMX Interactions

For HTMX-specific testing:

```python
async def test_htmx_component(self, browser_page):
    page = browser_page
    
    # Login and navigate
    user, login_success = await self.create_user_and_login(page)
    await page.goto(f"{self.config.server_url}/path/")
    
    # Find HTMX trigger and target
    trigger = page.locator('[hx-get="/api/data"]')
    target_id = await trigger.get_attribute('hx-target')
    
    # Trigger HTMX request
    await trigger.click()
    
    # Wait for HTMX request to complete
    await self.wait_for_htmx_request(page)
    
    # Verify the target was updated
    target = page.locator(target_id)
    assert await self.assert_element_contains_text(target, 'Expected response')
```

### Advanced Browser Agent Flows

For complex user flows using AI automation:

```python
async def test_ai_workflow(self):
    tasks = [
        f"Go to {self.config.server_url}/accounts/login/",
        "Login with username test and password password123",
        "Navigate to the todo list",
        "Create a new todo with title 'Test Task'",
        # ...more natural language instructions
    ]
    
    agent = BrowserAgent(
        tasks=tasks,
        browser_type=self.config.browser_type,
        headless=self.config.headless
    )
    
    result = await agent.run()
    assert "success" in result.lower()
```

## Screenshots and Debugging

Tests automatically capture screenshots at key points in the test execution, stored in the `test_screenshots` directory. To debug tests:

1. Set `headless = False` in `EndToEndTestConfig`
2. Set `slow_mo = 100` to slow down browser actions
3. Add additional screenshot captures with `await self.take_screenshot(page, "filename.png")`

## Best Practices

### General Best Practices

1. **Create dual-layer tests**: Implement both browser-based and standard Django tests for critical functionality
2. **Use namespaced URLs**: Reference URLs via reverse with namespace (`public:account-settings`) instead of hardcoded paths
3. **Isolate test data**: Create test users with unique identifiers (UUIDs) to avoid conflicts between test runs
4. **Check correct form context**: Verify form names in view code (`user_form` vs `form`) before writing assertions
5. **Check server availability**: Automatically skip browser tests when the Django server isn't running
6. **Verify database changes**: After form submissions, refresh model instances from the database to verify changes
7. **Use screenshots strategically**: Capture screenshots before/after key interactions for debugging
8. **Handle login & authentication**: Include robust login methods that detect success via multiple indicators
9. **Follow redirects**: Use `follow=True` on POST requests to follow redirects to destination pages
10. **Test admin interfaces**: Don't forget to test admin functionality, as it contains critical business logic
11. **Understand view implementations**: Study the view code to understand what context variables and form names to test

### HTMX-Specific Best Practices

1. **Wait for HTMX requests to complete**: Use `wait_for_htmx_request()` to ensure requests finish
2. **Verify both source and target elements**: Check both what triggers the HTMX action and what receives the update
3. **Test out-of-band updates**: Verify that multiple page sections update correctly
4. **Test admin interfaces**: Specially test the Django Unfold admin dashboard, which uses extensive HTMX
5. **Use data attributes**: Target data-* attributes rather than classes that might change with styling updates
6. **Look for text content changes**: After HTMX requests, check that the content has actually changed

### Test Structure Best Practices

1. **Organize by feature**: Create test files focused on specific features (account settings, admin, etc.)
2. **Use TestCase class suffix**: Name test classes with descriptive suffixes like `AccountSettingsTestCase`
3. **Separate client and browser tests**: Create separate classes for Django test client and browser tests
4. **Keep test methods focused**: Each test method should test one specific aspect of functionality
5. **Consistent fixtures**: Use setup methods that create similar test data in both test client and browser tests
6. **Handle missing dependencies**: Use try/except patterns to gracefully handle missing browser-use
7. **Include server availability check**: Automatically skip tests when local server isn't running
8. **Test method naming**: Use clear names like `test_update_profile_info` and `test_failed_validation_browser`
9. **Reuse login utilities**: Create reusable login helper methods to avoid code duplication

### Django Admin Testing

1. **Don't rely on fixed text**: Some admin interfaces (like Django Unfold) customize the admin text
2. **Check for model names**: Look for model names like "Users" instead of fixed text like "Site administration"
3. **Verify login/logout flows**: Test that admin login and logout flows work correctly
4. **Handle menu interactions**: In modern admin UIs, logout might be hidden in a user menu dropdown
5. **Use POST for logout**: Django admin logout requires POST, not GET requests

### Form Testing Best Practices

1. **Test both valid and invalid inputs**: Test form validation for both valid and invalid data
2. **Check form error messages**: Verify that appropriate error messages are displayed for invalid data
3. **Verify database updates**: After form submission, refresh models from the database to check changes
4. **Test form field states**: Verify field values, disabled states, and other field attributes
5. **Handle multiple forms**: Pay attention to pages with multiple forms (like account settings with profile and password forms)
6. **Check success messages**: Verify success messages appear after successful form submission

### Test Robustness

1. **Handle timing issues**: Use proper wait strategies rather than fixed time.sleep() calls
2. **Make tests deterministic**: Avoid relying on non-deterministic factors like animation timing
3. **Avoid dependencies between tests**: Each test should be completely independent
4. **Mock external services**: Use mocks for external API calls, email services, etc.
5. **Test error states**: Test how your UI responds to errors, not just happy paths
6. **Try multiple selectors**: For critical elements, provide multiple selector alternatives
7. **Use try/except in login**: Handle potential login page variations or login failures gracefully

## Limitations and Considerations

1. **Performance impact**: E2E tests are much slower than unit or integration tests
2. **Server requirement**: Tests require a running Django server instance
3. **Environment dependencies**: Tests may behave differently across operating systems
4. **Maintenance overhead**: E2E tests require more maintenance as the UI evolves
5. **Debugging complexity**: Failures can be harder to debug than simpler test types
6. **CI pipeline complexity**: Setting up E2E tests in CI environments requires additional configuration
7. **False positives/negatives**: E2E tests can sometimes fail due to timing issues rather than actual bugs
8. **Version compatibility**: browser-use requires Python 3.11+

## Extending the Framework

You can extend the E2E testing framework by:

1. Adding new helper methods to `E2ETestBase`
2. Creating fixture factories for complex test data
3. Adding specialized test classes for specific features
4. Implementing visual regression testing with screenshot comparison

## Example Implementations

### Todo Workflow Testing

See `apps/public/tests/test_todo_workflow.py` and `apps/public/tests/test_todo_visual.py` for comprehensive testing of the Todo feature:

1. **Standard Django Testing Approach (`test_todo_workflow.py`)**:
   - Creating a new Todo item
   - Verifying it appears in the list view
   - Marking it as complete
   - Verifying its status changes to "Done"
   - Testing with Django's test client for reliable assertions

2. **Visual Testing Approach (`test_todo_visual.py`)**:
   - Browser-based testing with Playwright
   - Visual verification through screenshots
   - Highlighting specific elements for documentation
   - Walking through the entire user workflow visually

3. **Manual Testing Helper (`test_todo_manual.py`)**:
   - Creating test users and sample data
   - Providing instructions for manual testing
   - Assisting in documentation creation
   - Useful for complex interactions that are difficult to automate

### Admin Interface Testing

See `apps/public/tests/test_admin_e2e.py` for testing the Django admin interface. This example demonstrates:

1. Testing login and logout flows with both Django test client and browser-use
2. Testing custom admin interfaces (Django Unfold)
3. Handling dropdown menus and complex UI interactions
4. Checking POST-based logout requirements

### Account Settings Testing

See `apps/public/tests/test_account_settings_e2e.py` for testing user account functionality:

1. Testing form submission and validation
2. Testing profile information updates
3. Testing password changing functionality
4. Verifying validation errors are displayed correctly
5. Working with email fields and validation

### Key Implementation Patterns

All examples showcase these important patterns:

1. **Multi-layer testing**: Using both Django's TestCase and browser-based tests for complete coverage
2. **Proper URL naming**: Using namespaced URLs (`public:todo-list`) instead of hardcoded URLs
3. **Form context variables**: Accessing the specific form context variables used in the view
4. **Server availability checking**: Automatically skipping tests when the server isn't running
5. **Screenshot capturing**: Taking screenshots at key points to aid debugging
6. **Unique test data**: Using UUIDs to generate unique test data for each test run
7. **Test isolation**: Each test performs its own setup and cleanup
8. **Flexible selectors**: Using multiple selector strategies to find elements reliably
9. **Error handling**: Gracefully handling failures with error screenshots

### Tips for Effective E2E Testing

1. **Start with Django client tests**: Always implement standard Django test client tests before browser tests. They're faster, more reliable, and easier to debug.

2. **Layer your testing strategy**:
   - Unit tests for model, utility, and service methods
   - Integration tests for views and form processing
   - Browser tests for UI workflows and HTMX interactions

3. **Handling authentication challenges**:
   - Use `client.force_login()` in Django tests
   - For browser tests, consider setting session cookies directly
   - Create specific test users with controlled permissions

4. **Avoiding flaky tests**:
   - Don't rely on exact CSS selectors that might change
   - Prefer data attributes or text content for element selection
   - Use flexible timeouts rather than fixed delays
   - Implement retry mechanisms for intermittent failures

5. **Troubleshooting browser tests**:
   - Use `headless=False` to watch the test in real-time
   - Capture screenshots at each step
   - Use `slow_mo` to slow down interactions for visibility
   - Print page content when elements aren't found

6. **Testing HTMX interactions**:
   - Wait for HTMX requests to complete before assertions
   - Verify both element interactions and resulting content
   - Test out-of-band updates to multiple page regions
   - Use adequate timeouts for complex HTMX workflows

7. **Documentation Integration**:
   - Use screenshot tests as part of your documentation process
   - Create dedicated screenshot directories by feature
   - Run visual tests before major releases to update docs

8. **Resource Considerations**:
   - Run E2E tests separately from unit/integration tests
   - Consider running a subset of critical E2E tests in CI
   - Use proper cleanup to avoid test database pollution

## Related Documentation

- [Browser-Use GitHub](https://github.com/browser-use/browser-use): Official repository
- [Playwright Python API](https://playwright.dev/python/docs/intro): Playwright documentation
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio): Async testing with pytest
- [HTMX_INTEGRATION.md](HTMX_INTEGRATION.md): HTMX integration reference
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/): Django's testing documentation