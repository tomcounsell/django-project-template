"""
Example end-to-end tests using browser-use.

These tests are simplified examples of how to use browser-use
for end-to-end testing in the Django Project Template. They 
depend on browser-use and playwright packages being installed.

To run these tests:
1. Start the Django server: python manage.py runserver
2. Run the tests: DJANGO_SETTINGS_MODULE=settings pytest apps/public/tests/test_e2e_example.py -v

Note: These tests are meant to run in local development only.
"""

import os
import pytest
import asyncio
from typing import Any, Dict, Optional, TYPE_CHECKING

# Try to import browser-use dependencies
try:
    import playwright.async_api
    import pytest_asyncio
    # Define Page type for type hints
    if TYPE_CHECKING:
        from playwright.async_api import Page
    else:
        Page = playwright.async_api.Page
    BROWSER_TESTING_AVAILABLE = True
    HAS_PYTEST_ASYNCIO = True
except ImportError:
    BROWSER_TESTING_AVAILABLE = False
    HAS_PYTEST_ASYNCIO = False
    # Create a dummy Page class for type hints when imports fail
    class Page: pass

# Define asyncio mark conditionally to avoid warnings
if HAS_PYTEST_ASYNCIO:
    asyncio_mark = pytest.mark.asyncio
else:
    # Create a no-op marker if pytest-asyncio is not available
    asyncio_mark = lambda f: f

# Skip all tests if browser testing packages aren't available
pytestmark = pytest.mark.skipif(
    not BROWSER_TESTING_AVAILABLE,
    reason="Browser testing packages not installed. Run: uv add --dev browser-use playwright pytest-asyncio"
)

# Skip if not in a pytest environment
if not hasattr(pytest, "mark"):
    pytestmark = lambda *args, **kwargs: lambda f: f  # noqa


@asyncio_mark
async def test_home_page_loads(async_page):
    """Test that the home page loads correctly."""
    # Skip if server is not running
    if not await is_server_running():
        pytest.skip("Django server not running at http://localhost:8000")
    
    # Navigate to the home page
    page = async_page
    await page.goto("http://localhost:8000/")
    
    # Take a screenshot
    os.makedirs("test_screenshots", exist_ok=True)
    await page.screenshot(path="test_screenshots/home_page.png")
    
    # Check that the page title is correct
    title = await page.title()
    assert "Django Project Template" in title
    
    # Check that the page has the expected content
    content = await page.content()
    assert "Django Project Template" in content


@asyncio_mark
async def test_login_form(async_page):
    """Test that the login form works correctly."""
    # Skip if server is not running
    if not await is_server_running():
        pytest.skip("Django server not running at http://localhost:8000")
    
    # Navigate to the login page
    page = async_page
    await page.goto("http://localhost:8000/accounts/login/")
    
    # Check that the login form is present
    assert await page.locator("form").count() > 0
    
    # Fill in the login form (with credentials that won't work)
    await page.fill('input[name="username"]', "testuser")
    await page.fill('input[name="password"]', "wrongpassword")
    
    # Take a screenshot before submitting
    await page.screenshot(path="test_screenshots/login_form_filled.png")
    
    # Submit the form
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle")
    
    # Take a screenshot after submitting
    await page.screenshot(path="test_screenshots/login_error.png")
    
    # Check that we get an error message
    error_text = await page.locator(".error").text() if await page.locator(".error").count() > 0 else ""
    assert "error" in error_text.lower() or "invalid" in error_text.lower()


# Helper function to check if the Django server is running
async def is_server_running() -> bool:
    """Check if the Django server is running at localhost:8000."""
    try:
        browser = await playwright.async_api.async_playwright().start()
        chromium = await browser.chromium.launch()
        page = await chromium.new_page()
        
        # Try to connect with a short timeout
        page.set_default_timeout(2000)
        try:
            await page.goto("http://localhost:8000/")
            result = True
        except:
            result = False
            
        # Clean up
        await page.close()
        await chromium.close()
        await browser.stop()
        
        return result
    except:
        return False