"""
E2E test for the todo workflow.

This test covers the full user workflow for creating, completing,
and deleting todo items using browser automation.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.e2e
@pytest.mark.workflow
def test_todo_create_complete_delete_flow(driver, live_server, db):
    """Test the complete workflow of creating, completing, and deleting a todo item."""
    # Navigate to the todo list page
    driver.get(f"{live_server.url}/todos/")

    # Get initial count of todo items
    todo_items = driver.find_elements(By.CSS_SELECTOR, ".todo-item")
    initial_count = len(todo_items)

    # Create a new todo item
    new_todo_title = "E2E Test Todo Item"
    create_new_todo(driver, new_todo_title)

    # Verify the new todo was created
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, ".todo-item")) > initial_count
    )

    # Find the new todo item
    todo_items = driver.find_elements(By.CSS_SELECTOR, ".todo-item")
    new_todo = None
    for item in todo_items:
        if new_todo_title in item.text:
            new_todo = item
            break

    assert new_todo is not None, f"Could not find newly created todo: {new_todo_title}"

    # Complete the todo item
    checkbox = new_todo.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
    checkbox.click()

    # Verify the todo item is marked as completed
    WebDriverWait(driver, 10).until(
        lambda d: "completed" in new_todo.get_attribute("class")
        or "line-through"
        in new_todo.find_element(By.CSS_SELECTOR, "span").get_attribute("class")
    )

    # Delete the todo item
    delete_button = new_todo.find_element(By.CSS_SELECTOR, "a[href*='delete']")
    delete_button.click()

    # Confirm deletion on the confirmation page
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
    )
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Verify we're back on the todo list page
    WebDriverWait(driver, 10).until(EC.url_contains("/todos/"))

    # Verify the todo item was deleted
    todo_items = driver.find_elements(By.CSS_SELECTOR, ".todo-item")
    assert len(todo_items) == initial_count, "Todo item was not deleted successfully"

    # Verify the deleted todo item is not in the list
    for item in todo_items:
        assert new_todo_title not in item.text, "Todo item still exists after deletion"


def create_new_todo(driver, title):
    """Helper function to create a new todo item."""
    # Click the "Add Todo" button/link
    try:
        add_button = driver.find_element(By.CSS_SELECTOR, "a[href*='add']")
        add_button.click()
    except:
        # Try alternate ways to find the add button
        add_button = driver.find_element(By.LINK_TEXT, "Add Todo")
        add_button.click()

    # Wait for the form to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id_title")))

    # Fill in the form
    title_input = driver.find_element(By.ID, "id_title")
    title_input.clear()
    title_input.send_keys(title)

    # Submit the form
    title_input.send_keys(Keys.RETURN)
