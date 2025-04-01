from django.test import TestCase, override_settings
from django.urls import reverse

from apps.common.models import TodoItem
from apps.common.tests.factories import UserFactory, TodoItemFactory


@override_settings(TESTING=True)
class TodoViewsTestCase(TestCase):
    """Test case for Todo views."""

    def setUp(self):
        # Use a unique username to avoid conflicts with other tests
        import uuid

        self.username = f"todouser_{uuid.uuid4().hex[:8]}"
        self.user = UserFactory.create(username=self.username, password="testpass123")

        # Create some test todo items
        self.todo1 = TodoItemFactory.create(
            title="Complete project documentation",
            priority="HIGH",
            category="DOCUMENTATION",
            status="TODO",
            assignee=self.user,
        )

        self.todo2 = TodoItemFactory.create(
            title="Fix API security issue",
            priority="HIGH",
            category="SECURITY",
            status="IN_PROGRESS",
            assignee=self.user,
        )

        self.todo3 = TodoItemFactory.create(
            title="Optimize database queries",
            priority="MEDIUM",
            category="PERFORMANCE",
            status="TODO",
            assignee=None,
        )

        # URLs
        self.todo_list_url = reverse("public:todo-list")
        self.todo_create_url = reverse("public:todo-create")
        self.todo_detail_url = reverse(
            "public:todo-detail", kwargs={"pk": self.todo1.id}
        )
        self.todo_update_url = reverse(
            "public:todo-update", kwargs={"pk": self.todo1.id}
        )
        self.todo_delete_url = reverse(
            "public:todo-delete", kwargs={"pk": self.todo1.id}
        )
        self.todo_complete_url = reverse(
            "public:todo-complete", kwargs={"pk": self.todo1.id}
        )

        # Login the test user
        self.client.login(username=self.username, password="testpass123")

    def test_todo_list_view(self):
        """Test the todo list view."""
        response = self.client.get(self.todo_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todos/todo_list.html")

        # Check that todos are in the context
        self.assertIn("todos", response.context)
        todos = response.context["todos"]

        # Verify our test todos are included (instead of checking exact count)
        todo_titles = [todo.title for todo in todos]
        self.assertIn(self.todo1.title, todo_titles)
        self.assertIn(self.todo2.title, todo_titles)
        self.assertIn(self.todo3.title, todo_titles)

        # Check title is displayed
        self.assertContains(response, "Complete project documentation")
        self.assertContains(response, "Fix API security issue")
        self.assertContains(response, "Optimize database queries")

    def test_todo_detail_view(self):
        """Test the todo detail view."""
        response = self.client.get(self.todo_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todos/todo_detail.html")

        # Check that the todo is in the context
        self.assertIn("todo", response.context)
        todo = response.context["todo"]
        self.assertEqual(todo.id, self.todo1.id)

        # Check content is displayed
        self.assertContains(response, self.todo1.title)
        self.assertContains(response, "HIGH")  # Priority
        self.assertContains(response, "DOCUMENTATION")  # Category

    def test_todo_create_view_get(self):
        """Test the GET request to the todo create view."""
        response = self.client.get(self.todo_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todos/todo_form.html")

        # Check that the form is in the context
        self.assertIn("form", response.context)

    def test_todo_create_view_post(self):
        """Test the POST request to the todo create view."""
        data = {
            "title": "Test New Todo Item",
            "description": "This is a test todo item",
            "priority": "MEDIUM",
            "category": "TESTING",
            "status": "TODO",
        }

        response = self.client.post(self.todo_create_url, data, follow=True)
        self.assertRedirects(response, self.todo_list_url)

        # Check that the todo was created
        self.assertTrue(TodoItem.objects.filter(title="Test New Todo Item").exists())
        new_todo = TodoItem.objects.get(title="Test New Todo Item")
        self.assertEqual(new_todo.description, "This is a test todo item")
        self.assertEqual(new_todo.priority, "MEDIUM")
        self.assertEqual(new_todo.category, "TESTING")
        self.assertEqual(new_todo.status, "TODO")

        # Check that current user is assigned
        self.assertEqual(new_todo.assignee, self.user)

    def test_todo_update_view_get(self):
        """Test the GET request to the todo update view."""
        response = self.client.get(self.todo_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todos/todo_form.html")

        # Check that the form is in the context with initial data
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertEqual(form.initial["title"], "Complete project documentation")

    def test_todo_update_view_post(self):
        """Test the POST request to the todo update view."""
        data = {
            "title": "Updated Todo Title",
            "description": "Updated description",
            "priority": "LOW",
            "category": "GENERAL",
            "status": "IN_PROGRESS",
        }

        response = self.client.post(self.todo_update_url, data, follow=True)
        self.assertRedirects(response, self.todo_detail_url)

        # Check that the todo was updated
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, "Updated Todo Title")
        self.assertEqual(self.todo1.description, "Updated description")
        self.assertEqual(self.todo1.priority, "LOW")
        self.assertEqual(self.todo1.category, "GENERAL")
        self.assertEqual(self.todo1.status, "IN_PROGRESS")

    def test_todo_delete_view_get(self):
        """Test the GET request to the todo delete view."""
        response = self.client.get(self.todo_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todos/todo_confirm_delete.html")

        # Check that the todo is in the context
        self.assertIn("todo", response.context)
        self.assertEqual(response.context["todo"].id, self.todo1.id)

    def test_todo_delete_view_post(self):
        """Test the POST request to the todo delete view."""
        response = self.client.post(self.todo_delete_url, follow=True)
        self.assertRedirects(response, self.todo_list_url)

        # Check that the todo was deleted
        self.assertFalse(TodoItem.objects.filter(id=self.todo1.id).exists())

    def test_todo_complete_view(self):
        """Test the todo complete view."""
        response = self.client.post(self.todo_complete_url, follow=True)
        self.assertRedirects(response, self.todo_detail_url)

        # Check that the todo was marked as completed
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.status, "DONE")
        self.assertIsNotNone(self.todo1.completed_at)

    def test_access_control(self):
        """Test that unauthenticated users are redirected to login."""
        # Logout the test user
        self.client.logout()

        # Check that unauthenticated users are redirected to login
        response = self.client.get(self.todo_list_url)
        self.assertRedirects(response, f"/account/login?next={self.todo_list_url}")
