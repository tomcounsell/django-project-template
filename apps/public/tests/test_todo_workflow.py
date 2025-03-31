"""
Test the Todo workflow using the Django test client.

This test focuses on the functional aspects of the Todo workflow:
1. Creating a new todo item
2. Viewing it in the list
3. Marking it as complete
4. Verifying its status is updated
5. Deleting the todo item
6. Verifying it's removed from the list
"""

import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

from apps.common.models import TodoItem

User = get_user_model()

@pytest.mark.django_db
def test_todo_complete_workflow():
    """
    Test the complete Todo workflow from creation to completion to deletion.
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
    # Add HTMX headers for the request
    response = client.post(
        reverse('public:todo-complete', kwargs={'pk': todo.id}),
        follow=True,
        HTTP_HX_REQUEST='true',  # Indicate this is an HTMX request
        HTTP_HX_TARGET=f'#todo-row-{todo.id}'  # Target the specific todo row
    )
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
    
    # Step 5: Delete the todo
    # First we need to get the modal content
    response = client.get(
        reverse('public:todo-delete-modal', kwargs={'pk': todo.id}),
        HTTP_HX_REQUEST='true',
        HTTP_REFERER=reverse('public:todo-list')
    )
    assert response.status_code == 200
    
    # Now submit the delete request with HTMX headers
    response = client.post(
        reverse('public:todo-delete', kwargs={'pk': todo.id}), 
        {'redirect_after': reverse('public:todo-list')},
        follow=True,
        HTTP_HX_REQUEST='true',
        HTTP_REFERER=reverse('public:todo-list')
    )
    assert response.status_code == 200
    
    # Step 6: Verify the todo is deleted
    assert TodoItem.objects.filter(pk=todo.id).count() == 0
    
    # Check that it's not in the list anymore
    response = client.get(reverse('public:todo-list'))
    assert response.status_code == 200
    content = response.content.decode()
    
    # Instead of checking for absence of the title (which could be in success messages),
    # Check that there are no todo rows containing the title
    assert f'<tr id="todo-row-{todo.id}"' not in content
    
    # Let's also verify the count in the database to be sure
    assert TodoItem.objects.filter(title='Test Todo Item').count() == 0
    
    print("Todo workflow test completed successfully!")