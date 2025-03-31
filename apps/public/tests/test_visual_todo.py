"""
Visual tests for the todo feature.

This module contains tests that verify the visual appearance of todo items
and their various states (completed, pending, etc).
"""

import os
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.visual
def test_todo_item_appearance(driver, live_server, db):
    """Test the visual appearance of todo items."""
    # Navigate to the todo list page
    driver.get(f"{live_server.url}/todos/")
    
    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )
    
    # Verify todo container has expected styles
    todo_container = driver.find_element(By.CSS_SELECTOR, ".todo-container")
    container_class = todo_container.get_attribute("class")
    
    # Basic checks for container styling
    assert "w-full" in container_class or "container" in container_class, "Todo container should have proper width class"
    
    # Check for todo items
    todo_items = driver.find_elements(By.CSS_SELECTOR, ".todo-item")
    
    if todo_items:
        # Check first todo item styling
        todo_item = todo_items[0]
        item_class = todo_item.get_attribute("class")
        
        # Todo items should have padding and margins
        assert any(c in item_class for c in ["p-", "py-", "px-"]), "Todo item should have padding"
        assert any(c in item_class for c in ["m-", "my-", "mx-"]), "Todo item should have margin"
        
        # Todo items should have proper text size
        text_element = todo_item.find_element(By.CSS_SELECTOR, "span")
        text_class = text_element.get_attribute("class")
        assert any(c in text_class for c in ["text-", "font-"]), "Todo text should have style classes"
        
        # Verify checkbox is present and styled
        checkbox = todo_item.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        assert checkbox.is_displayed(), "Checkbox should be visible"
        
        # Verify actions (edit/delete) are present
        action_links = todo_item.find_elements(By.CSS_SELECTOR, "a")
        assert len(action_links) >= 1, "Todo item should have action links"
    
    # Take a screenshot for visual inspection
    screenshot_path = "reports/screenshots/todo_list.png"
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    driver.save_screenshot(screenshot_path)


@pytest.mark.visual
def test_completed_todo_appearance(driver, live_server, db):
    """Test the visual appearance of completed todo items."""
    from apps.common.models.todo import TodoItem
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Create a test user
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Create a completed todo item
    TodoItem.objects.create(
        title="Completed Todo Item",
        user=user,
        completed=True
    )
    
    # Navigate to the todo list page
    driver.get(f"{live_server.url}/todos/")
    
    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".todo-item"))
    )
    
    # Find completed todo items
    completed_todos = driver.find_elements(By.CSS_SELECTOR, ".todo-item.completed")
    
    if not completed_todos:
        # Try alternate class structure
        completed_todos = []
        todo_items = driver.find_elements(By.CSS_SELECTOR, ".todo-item")
        for item in todo_items:
            text_element = item.find_element(By.CSS_SELECTOR, "span")
            if "line-through" in text_element.get_attribute("class"):
                completed_todos.append(item)
    
    assert len(completed_todos) > 0, "No completed todo items found"
    
    # Verify completed todo has distinct styling
    completed_todo = completed_todos[0]
    text_element = completed_todo.find_element(By.CSS_SELECTOR, "span")
    text_class = text_element.get_attribute("class")
    
    # Completed todos should have line-through or other distinctive styling
    has_completed_style = (
        "line-through" in text_class or
        "completed" in text_class or
        "text-gray" in text_class
    )
    assert has_completed_style, "Completed todo should have distinctive styling"
    
    # Take a screenshot for visual inspection
    screenshot_path = "reports/screenshots/completed_todo.png"
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    driver.save_screenshot(screenshot_path)