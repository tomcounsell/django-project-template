"""
Generate screenshots of the Todo workflow.

This script uses Django's test client to execute the Todo workflow
and capture screenshots at each step for documentation.
"""

import os
import uuid
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from apps.common.models import TodoItem

# Try to import Playwright for screenshots
try:
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

User = get_user_model()


def capture_url(url, output_path, cookies=None):
    """Capture screenshot of a URL using headless browser."""
    if not PLAYWRIGHT_AVAILABLE:
        print(f"Playwright not available. Cannot capture {url}")
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1280, "height": 800})

            # Add cookies if provided
            if cookies:
                for cookie in cookies:
                    context.add_cookies([cookie])

            page = context.new_page()
            page.goto(url)

            # Wait for the page to be fully loaded
            try:
                page.wait_for_load_state("networkidle", timeout=3000)
            except:
                # Continue if timeout occurs
                print(f"Timeout waiting for page to load: {url}")

            # Wait additional time to ensure rendering
            page.wait_for_timeout(1000)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            page.screenshot(path=output_path)
            browser.close()
            return True
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return False


@pytest.mark.django_db
def test_generate_todo_screenshots():
    """Generate screenshots of the Todo workflow using Django test client."""
    screenshots_dir = "test_screenshots/workflow"
    os.makedirs(screenshots_dir, exist_ok=True)
    server_url = "http://localhost:8080"  # Local dev server for screenshots

    # Create test user
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpassword123"
    user = User.objects.create_user(
        username=username, email=f"{username}@example.com", password=password
    )

    # Set up test client and log in
    client = Client()
    client.force_login(user)

    # Step 1: Todo List (Empty)
    response = client.get(reverse("public:todo-list"))
    assert response.status_code == 200
    print(f"Step 1: Viewing empty todo list")
    capture_url(f"{server_url}/todos/", f"{screenshots_dir}/01_todo_list_empty.png")

    # Step 2: Create Todo Form
    response = client.get(reverse("public:todo-create"))
    assert response.status_code == 200
    print(f"Step 2: Viewing create todo form")
    capture_url(
        f"{server_url}/todos/create/", f"{screenshots_dir}/02_todo_create_form.png"
    )

    # Step 3: Creating a new Todo
    todo_title = f"Screenshot Todo {uuid.uuid4().hex[:6]}"
    todo_data = {
        "title": todo_title,
        "description": "This is a test todo for screenshots",
        "priority": "HIGH",
        "category": "TESTING",
        "status": "TODO",
    }
    response = client.post(reverse("public:todo-create"), todo_data, follow=True)
    assert response.status_code == 200
    todo = TodoItem.objects.get(title=todo_title)
    print(f"Step 3: Created todo: {todo_title} (ID: {todo.id})")

    # Step 4: View Todo List with new item
    response = client.get(reverse("public:todo-list"))
    assert response.status_code == 200
    print(f"Step 4: Viewing todo list with new item")
    capture_url(f"{server_url}/todos/", f"{screenshots_dir}/03_todo_list_with_item.png")

    # Step 5: View Todo Detail
    response = client.get(reverse("public:todo-detail", kwargs={"pk": todo.id}))
    assert response.status_code == 200
    print(f"Step 5: Viewing todo detail page")
    capture_url(
        f"{server_url}/todos/{todo.id}/", f"{screenshots_dir}/04_todo_detail.png"
    )

    # Step 6: Mark Todo as Complete
    response = client.post(
        reverse("public:todo-complete", kwargs={"pk": todo.id}), follow=True
    )
    assert response.status_code == 200
    todo.refresh_from_db()
    assert todo.status == "DONE"
    print(f"Step 6: Marked todo as complete")
    capture_url(
        f"{server_url}/todos/{todo.id}/",
        f"{screenshots_dir}/05_todo_completed_detail.png",
    )

    # Step 7: View Todo List with completed item
    response = client.get(reverse("public:todo-list"))
    assert response.status_code == 200
    print(f"Step 7: Viewing todo list with completed item")
    capture_url(
        f"{server_url}/todos/", f"{screenshots_dir}/06_todo_list_with_completed.png"
    )

    print(f"Todo workflow screenshots generated successfully in {screenshots_dir}/")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
