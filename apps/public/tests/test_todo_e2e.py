"""
End-to-end tests for the Todo feature using browser-use and Playwright.

This file tests the complete workflow for a user working with Todo items:
1. User logs in
2. Navigates to the Todo list page
3. Creates a new Todo item
4. Verifies the item appears in the list
5. Marks the Todo item as complete
6. Verifies the item is marked as complete
7. Deletes the Todo item
8. Verifies the item is removed from the list
"""

import os
import pytest
import asyncio
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING
import uuid
import time

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

# Import pytest-asyncio
import pytest_asyncio

# Import browser-use components
try:
    from browser_use import Agent, BrowserAgent
    import playwright.async_api
    # Define Page type for type hints
    if TYPE_CHECKING:
        from playwright.async_api import Page
    else:
        Page = playwright.async_api.Page
    BROWSER_USE_AVAILABLE = True
    HAS_PYTEST_ASYNCIO = True
    
    # Import the base test class 
    from .test_e2e_patterns import E2ETestBase, browser_test, asyncio_mark
except ImportError:
    BROWSER_USE_AVAILABLE = False
    HAS_PYTEST_ASYNCIO = False
    # Create a dummy Page class for type hints when imports fail
    class Page: pass
    
    # Create dummy markers for compatibility
    browser_test = lambda cls: cls
    asyncio_mark = lambda f: f
    
    # Create dummy base class
    class E2ETestBase:
        pass

# Add database mark
pytestmark = [
    pytest.mark.django_db  # Allow database access
]

# Test server URL
SERVER_URL = "http://localhost:8000"

User = get_user_model()

# Create fixtures for browser and page
@pytest_asyncio.fixture
async def browser():
    """Create a browser instance for testing."""
    playwright_instance = await playwright.async_api.async_playwright().start()
    browser_instance = await playwright_instance.chromium.launch(
        headless=False,  # Set to True for CI/production, False for local debugging
        slow_mo=100,  # Slow down operations so we can see what's happening
    )
    yield browser_instance
    await browser_instance.close()
    await playwright_instance.stop()

@pytest_asyncio.fixture
async def page(browser):
    """Create a page for testing."""
    context = await browser.new_context(viewport={'width': 1280, 'height': 800})
    page = await context.new_page()
    # Set default timeout
    page.set_default_timeout(5000)
    yield page
    await context.close()

@pytest.fixture
def test_user(django_db_setup):
    """Create a test user for login."""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpassword123"
    user = User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password=password
    )
    return user, username, password

@browser_test
@asyncio_mark
class TestTodoCompleteWorkflow(E2ETestBase):
    """Test the complete workflow for Todo items."""
    
    async def test_todo_workflow_with_agent(self, test_user):
        """
        Test the complete workflow for Todo items using browser-use AI agent.
        
        This tests:
        1. Login to the application
        2. Navigate to the Todo list
        3. Create a new Todo
        4. Verify it appears in the list
        5. Mark it as complete
        6. Verify it's marked as complete
        7. Delete the Todo
        8. Verify it's removed from the list
        """
        # Skip if browser-use is not available
        if not BROWSER_USE_AVAILABLE:
            pytest.skip("browser-use package not installed")
        
        # Get test user credentials
        user, username, password = test_user
        todo_title = f"Test Todo {uuid.uuid4().hex[:8]}"
        
        # Create screenshots directory
        screenshots_dir = "test_screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Define tasks for the browser agent
        tasks = [
            f"Go to {SERVER_URL}/account/login",
            f"Login with username '{username}' and password '{password}'",
            
            # Navigate to Todo list
            "Navigate to the Todo list page by clicking on 'Todo List' in the navigation or going to /todos/",
            
            # Create Todo
            "Click on 'Create New Todo' button",
            f"Fill in the title field with '{todo_title}'",
            "Select 'High' for priority if available",
            "Write a description 'This is a test todo created by browser-use agent'",
            "Click on Save/Submit button",
            "Wait for the page to load and confirm we're back on the todo list",
            
            # Take a screenshot
            f"Take a screenshot and save it to {screenshots_dir}/todo_created.png",
            
            # Verify Todo exists
            f"Verify that a todo with title '{todo_title}' appears in the list",
            
            # Complete Todo
            f"Find the todo item with title '{todo_title}' and click on the 'Complete' button next to it",
            "Wait for the row to update",
            
            # Take a screenshot
            f"Take a screenshot and save it to {screenshots_dir}/todo_completed.png",
            
            # Verify Todo is completed
            f"Verify that the todo with title '{todo_title}' is now marked as 'Done' or 'Completed'",
            
            # Delete Todo
            f"Find the todo item with title '{todo_title}' and click on the 'Delete' button next to it",
            "In the confirmation modal that appears, click on 'Delete' to confirm",
            "Wait for the todo to be removed from the list",
            
            # Take a screenshot
            f"Take a screenshot and save it to {screenshots_dir}/todo_deleted.png",
            
            # Verify Todo is deleted
            f"Verify that the todo with title '{todo_title}' is no longer in the list",
        ]
        
        # Create browser agent to perform tasks
        agent = BrowserAgent(
            tasks=tasks,
            browser_type="chromium",
            headless=False,  # Show the browser for debugging
            screenshot_dir=screenshots_dir,
        )
        
        # Run the agent and get the result
        result = await agent.run()
        print(f"Browser agent result: {result}")
        
        # Assert the agent completed successfully
        assert "success" in result.lower() or "completed" in result.lower(), f"Browser agent failed: {result}"
        
        # Verify the todo doesn't exist in the database
        from apps.common.models import TodoItem
        todos = TodoItem.objects.filter(title=todo_title)
        assert not todos.exists(), f"Todo with title '{todo_title}' still exists in database"
        
        print(f"Successfully completed end-to-end test for todo item: {todo_title}")

@pytest.mark.asyncio
async def test_todo_complete_workflow_manual(page, test_user):
    """
    Manual implementation of the todo workflow test without browser-use agent.
    
    Tests the complete workflow for Todo items:
    1. Login
    2. Navigate to Todo list
    3. Create a new Todo
    4. Verify it appears in the list
    5. Mark it as complete
    6. Verify it's marked as complete
    7. Delete the Todo
    8. Verify it's removed from the list
    """
    user, username, password = test_user
    
    try:
        # Define unique todo title
        todo_title = f"Test Todo {uuid.uuid4().hex[:8]}"
        print(f"Testing with todo title: {todo_title}")
        
        # Login
        await login(page, username, password)
        
        # Step 2: Navigate to the Todo list page
        print("Navigating to Todo list page...")
        await page.goto(f"{SERVER_URL}/todos/")
        await page.wait_for_timeout(2000)
        
        # Take screenshot of Todo list page
        await take_screenshot(page, "todo_test_list_page.png")
        
        # Step 3: Create a new Todo item
        print("Creating new Todo item...")
        
        # Find and click the create button
        await page.click("text=Create New Todo")
        await page.wait_for_timeout(2000)
        
        # Fill out the form
        await page.fill("input[id*='title'], input[name*='title']", todo_title)
        
        # Try to fill description if it exists
        desc_field = page.locator("textarea[id*='description'], textarea[name*='description']")
        if await desc_field.count() > 0:
            await desc_field.fill("This is a test todo item created by E2E test.")
        
        # Try to select High priority if field exists
        priority_field = page.locator("select[id*='priority'], select[name*='priority']")
        if await priority_field.count() > 0:
            await priority_field.select_option("HIGH")
        
        # Take screenshot of filled form
        await take_screenshot(page, "todo_test_create_form.png")
        
        # Submit the form
        await page.click("button[type='submit']")
        await page.wait_for_timeout(2000)
        
        # Step 4: Verify the item appears in the list
        print("Verifying new todo appears in list...")
        
        # We might be on the list or detail page, navigate to list to be sure
        await page.goto(f"{SERVER_URL}/todos/")
        await page.wait_for_timeout(2000)
        
        # Take screenshot after creation
        await take_screenshot(page, "todo_test_after_create.png")
        
        # Verify the todo is in the list
        todo_row = page.locator(f"tr:has-text('{todo_title}')")
        assert await todo_row.count() > 0, f"Todo with title '{todo_title}' not found in list"
        
        # Step 5: Mark the Todo item as complete
        print("Marking todo as complete...")
        
        # Find and click the Complete button
        complete_button = todo_row.locator("text=Complete")
        await complete_button.click()
        await page.wait_for_timeout(2000)
        
        # Step 6: Verify the item is marked as complete
        print("Verifying todo is marked as complete...")
        
        # Take screenshot after completion
        await take_screenshot(page, "todo_test_completed.png")
        
        # Find our todo row again (it may have been updated by HTMX)
        todo_row = page.locator(f"tr:has-text('{todo_title}')")
        
        # Check if status shows Done (usually in the 4th column)
        status_cell = todo_row.locator("td:nth-child(4)")
        status_text = await status_cell.inner_text()
        assert "Done" in status_text, f"Todo status is '{status_text}', not 'Done'"
        
        # Verify the Complete button is no longer present
        complete_button = todo_row.locator("text=Complete")
        assert await complete_button.count() == 0, "Complete button still visible for completed todo"
        
        # Step 7: Delete the Todo item
        print("Deleting todo...")
        
        # Find and click the Delete button
        delete_button = todo_row.locator("text=Delete")
        await delete_button.click()
        await page.wait_for_timeout(1000)
        
        # Confirm deletion in the modal
        confirm_delete = page.locator("button:has-text('Delete')").nth(1)  # Get the second Delete button (in modal)
        await confirm_delete.click()
        await page.wait_for_timeout(2000)
        
        # Take screenshot after deletion
        await take_screenshot(page, "todo_test_deleted.png")
        
        # Step 8: Verify the item is removed from the list
        print("Verifying todo is deleted...")
        
        # Check that the todo is no longer in the list
        todo_row = page.locator(f"tr:has-text('{todo_title}')")
        assert await todo_row.count() == 0, f"Todo with title '{todo_title}' still present in list after deletion"
        
        print(f"Successfully tested complete todo workflow with todo: {todo_title}")
    
    except Exception as e:
        # Take a final screenshot if any error occurs
        await take_screenshot(page, "todo_test_error.png")
        print(f"Error during test: {str(e)}")
        raise

async def login(page, username, password):
    """Helper to log in a user."""
    # Navigate to login page
    await page.goto(f"{SERVER_URL}/account/login")
    
    # Wait for page to load
    try:
        await page.wait_for_load_state("networkidle", timeout=5000)
    except Exception as e:
        print(f"Warning: Wait for load state timed out: {e}")
    
    # Check if page loaded by verifying form presence
    if await page.locator("form").count() == 0:
        # Take screenshot for debugging
        await take_screenshot(page, "login_page_error.png")
        print("Login form not found, checking HTML content")
        content = await page.content()
        print(f"Page content excerpt: {content[:200]}...")
    
    # Fill the login form
    await page.fill("input[name=username]", username)
    await page.fill("input[name=password]", password)
    
    # Take screenshot before submitting
    await take_screenshot(page, "before_login_submit.png")
    
    # Submit the form
    await page.click("button[type=submit]")
    
    # Wait with simple timeout
    await page.wait_for_timeout(3000)
    
    # Take screenshot after submitting
    await take_screenshot(page, "after_login_submit.png")
    
    # Check if login was successful
    current_url = page.url
    print(f"After login, current URL: {current_url}")
    
    # Look for logout form or account menu
    has_logout = await page.locator("form.logout-form").count() > 0
    has_user_menu = await page.locator(".user-menu, .account-menu").count() > 0
    
    if not (has_logout or has_user_menu):
        # If we can't find logout link, check if we're on a protected page
        if "/todos/" in current_url or "/account/settings" in current_url:
            print("Login appears successful based on URL")
            return
        
        await take_screenshot(page, "login_failed.png")
        raise AssertionError(f"Login verification failed. Current URL: {current_url}")
    
    print("Login successful!")

async def take_screenshot(page, filename):
    """Helper to take a screenshot and save it to the screenshots directory."""
    screenshots_dir = "test_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    await page.screenshot(path=os.path.join(screenshots_dir, filename))
    return os.path.join(screenshots_dir, filename)