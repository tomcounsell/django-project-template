"""
Test the Todo workflow using the Django test client.

This test focuses on the functional aspects of the Todo workflow:
1. Creating a new todo item
2. Viewing it in the list
3. Marking it as complete
4. Verifying its status is updated
"""

import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

from apps.common.models import TodoItem

User = get_user_model()

@pytest.mark.django_db
def test_todo_workflow():
    """
    Test the complete Todo workflow from creation to completion.
    """
    # Create test user with unique username
    import uuid
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="testpassword123"
    )
    
    # Set up the test client
    client = Client()
    client.force_login(user)
    
    # Step 1: Create a new todo
    todo_data = {
        'title': 'Test Todo Item',
        'description': 'This is a test todo item',
        'priority': 'HIGH',
        'category': 'TESTING',
        'status': 'TODO',
    }
    response = client.post(reverse('public:todo-create'), todo_data, follow=True)
    
    # Verify successful creation - should be redirected to todo list
    assert response.status_code == 200
    assert 'Test Todo Item' in response.content.decode()
    
    # Get the todo from the database
    todo = TodoItem.objects.get(title='Test Todo Item')
    assert todo is not None
    assert todo.title == 'Test Todo Item'
    assert todo.priority == 'HIGH'
    assert todo.status == 'TODO'
    
    # Step 2: Visit the todo detail page
    response = client.get(reverse('public:todo-detail', kwargs={'pk': todo.id}))
    assert response.status_code == 200
    assert todo.title in response.content.decode()
    
    # Step 3: Mark the todo as complete
    response = client.post(reverse('public:todo-complete', kwargs={'pk': todo.id}), follow=True)
    assert response.status_code == 200
    
    # Step 4: Verify the todo is now complete
    todo.refresh_from_db()
    assert todo.status == 'DONE'
    assert todo.completed_at is not None
    
    # Check the list view to see if it shows as completed
    response = client.get(reverse('public:todo-list'))
    assert response.status_code == 200
    content = response.content.decode()
    assert todo.title in content
    assert 'Done' in content  # The status "Done" should appear in the list
    
    # Verify the complete button is no longer present for this todo
    assert f'todos/{todo.id}/complete' not in content
    
    print("Todo workflow test completed successfully!")