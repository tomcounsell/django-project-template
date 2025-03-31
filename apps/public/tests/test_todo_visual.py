"""
Visual test for Todo workflows using browser-use.

This file demonstrates how to use browser-use to create a visual test
of the Todo item workflow, which includes:
1. Creating a new Todo
2. Verifying it appears in the list
3. Completing the Todo
4. Deleting the Todo
"""

import os
import pytest
import asyncio
import uuid
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.urls import reverse

# Import pytest-asyncio
import pytest_asyncio

# Import browser-use components if available
try:
    # Try to import browser-use
    from browser_use import Agent, BrowserAgent
    BROWSER_USE_AVAILABLE = True
except ImportError:
    BROWSER_USE_AVAILABLE = False

# Skip tests if browser-use is not available
pytestmark = pytest.mark.skipif(
    not BROWSER_USE_AVAILABLE,
    reason="browser-use not installed. Run: pip install browser-use"
)

# Server URL for testing
SERVER_URL = "http://localhost:8000"

# Get User model
User = get_user_model()

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_todo_visual_workflow_with_agent():
    """Test the visual workflow of Todo using browser-use agent."""
    # Skip if browser-use is not available
    if not BROWSER_USE_AVAILABLE:
        pytest.skip("browser-use package not installed")
    
    # Create test user with unique username
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpassword123"
    user = User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password=password
    )
    
    # Create a unique todo title
    todo_title = f"Test Todo {uuid.uuid4().hex[:8]}"
    
    # Create screenshots directory
    screenshots_dir = "test_screenshots/visual"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Define tasks for the browser agent
    tasks = [
        f"Go to {SERVER_URL}/account/login",
        f"Login with username '{username}' and password '{password}'",
        
        # Navigate to Todo list
        "Navigate to the Todo list page by clicking on 'Todo List' in the navigation or going to /todos/",
        
        # Take a screenshot of the empty todo list
        f"Take a screenshot and save it to {screenshots_dir}/01_todo_list_empty.png",
        
        # Create Todo
        "Click on 'Create New Todo' button",
        f"Fill in the title field with '{todo_title}'",
        "Select 'High' for priority if available",
        "Write a description 'This is a test todo created by browser-use agent'",
        "Click on Save/Submit button",
        "Wait for the page to load and confirm we're back on the todo list",
        
        # Take a screenshot of the list with the new todo
        f"Take a screenshot and save it to {screenshots_dir}/02_todo_created.png",
        
        # Complete the Todo item
        f"Find the todo item with title '{todo_title}' and click on the 'Complete' button next to it",
        "Wait for the row to update",
        
        # Take a screenshot of the completed todo
        f"Take a screenshot and save it to {screenshots_dir}/03_todo_completed.png",
        
        # Delete the Todo item
        f"Find the todo item with title '{todo_title}' and click on the 'Delete' button next to it",
        "Wait for the confirmation modal to appear",
        f"Take a screenshot of the modal and save it to {screenshots_dir}/04_delete_modal.png",
        "In the confirmation modal that appears, click on 'Delete' to confirm",
        "Wait for the todo to be removed from the list",
        
        # Take a final screenshot showing the list after deletion
        f"Take a screenshot and save it to {screenshots_dir}/05_todo_deleted.png",
    ]
    
    # Create browser agent to run the tasks
    agent = BrowserAgent(
        tasks=tasks,
        browser_type="chromium",
        headless=False,  # Show the browser for this visual test
        screenshot_dir=screenshots_dir,
    )
    
    # Run the agent
    result = await agent.run()
    print(f"Browser agent result: {result}")
    
    # Assert the agent completed successfully
    assert "success" in result.lower() or "completed" in result.lower(), f"Browser agent failed: {result}"
    
    # Verify screenshots were created
    expected_screenshots = [
        "01_todo_list_empty.png",
        "02_todo_created.png", 
        "03_todo_completed.png",
        "04_delete_modal.png", 
        "05_todo_deleted.png"
    ]
    
    for screenshot in expected_screenshots:
        screenshot_path = os.path.join(screenshots_dir, screenshot)
        assert os.path.exists(screenshot_path), f"Expected screenshot {screenshot} was not created"
    
    print(f"Visual test completed successfully with {len(expected_screenshots)} screenshots in {screenshots_dir}")
    
    # Return the paths to the screenshots for display in the documentation
    return [os.path.join(screenshots_dir, s) for s in expected_screenshots]