"""
Manually document the Todo workflow with screenshots.

This is a script to help manually generate screenshots
for the Todo workflow documentation. It's designed to be
run from the command line and creates a test user that
can be used to manually go through the workflow while
capturing the screen.
"""

import os
import random
import uuid
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.common.models import TodoItem

# Define the screenshot directory
SCREENSHOTS_DIR = "test_screenshots/manual"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def create_test_user():
    """Create a test user for the manual workflow."""
    User = get_user_model()
    username = f"testuser_{uuid.uuid4().hex[:5]}"
    password = "password123"

    # Delete any existing test users to avoid cluttering the database
    User.objects.filter(username__startswith="testuser_").delete()

    # Create a new test user
    user = User.objects.create_user(
        username=username, email=f"{username}@example.com", password=password
    )

    print(f"\n✅ Created test user:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   User ID: {user.id}")

    return user


def create_sample_todos(user, count=3):
    """Create some sample todos for the user."""
    # Clear existing todos for this user
    TodoItem.objects.filter(assignee=user).delete()

    priorities = ["HIGH", "MEDIUM", "LOW"]
    categories = ["GENERAL", "FRONTEND", "BACKEND", "TESTING"]
    statuses = ["TODO", "IN_PROGRESS"]

    todos = []
    for i in range(count):
        todo = TodoItem.objects.create(
            title=f"Sample Todo {i+1}",
            description=f"This is a sample todo item {i+1} for testing",
            priority=random.choice(priorities),
            category=random.choice(categories),
            status=random.choice(statuses),
            assignee=user,
        )
        todos.append(todo)

    print(f"\n✅ Created {count} sample todos:")
    for todo in todos:
        print(f"   - {todo.title} (ID: {todo.id}, Status: {todo.status})")

    return todos


def print_instructions():
    """Print instructions for manually taking screenshots."""
    print("\n📸 SCREENSHOT INSTRUCTIONS:")
    print("   1. Log in with the user credentials above")
    print("   2. Navigate to the Todo list page")
    print("   3. Create a new Todo item")
    print("   4. View the Todo list with the new item")
    print("   5. View the Todo detail page")
    print("   6. Mark the Todo as complete")
    print("   7. View the Todo list with the completed item")
    print("\n   Save screenshots to:", SCREENSHOTS_DIR)
    print("\n👉 URL: http://localhost:8080/account/login")


if __name__ == "__main__":
    print("\n🚀 Todo Workflow Manual Screenshot Generator")
    print("===========================================")

    # Create resources
    user = create_test_user()
    todos = create_sample_todos(user, count=2)

    # Print instructions
    print_instructions()

    print("\n✅ Done! You can now start taking screenshots manually.")
    print("   Press Ctrl+C to exit when finished.")

    # Keep the script running
    try:
        input("\nPress Enter to exit...\n")
    except KeyboardInterrupt:
        print("\n\nExiting...")
