import unittest.mock
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.common.models import TodoItem, User
from apps.common.tests.factories import UserFactory


class TodoItemModelTestCase(TestCase):
    """Test case for TodoItem model."""

    def setUp(self):
        self.user = UserFactory.create()
        self.todo = TodoItem.objects.create(
            title="Implement error handling",
            description="Add proper error handling to the API endpoints",
            priority="HIGH",
            category="API",
            assignee=self.user,
            status="TODO",
        )

    # Testing base fields
    def test_todo_creation(self):
        """Test that a todo item can be created."""
        self.assertIsNotNone(self.todo.id)
        self.assertEqual(self.todo.title, "Implement error handling")
        self.assertEqual(
            self.todo.description, "Add proper error handling to the API endpoints"
        )
        self.assertEqual(self.todo.priority, "HIGH")
        self.assertEqual(self.todo.category, "API")
        self.assertEqual(self.todo.assignee, self.user)
        self.assertEqual(self.todo.status, "TODO")

    def test_todo_str_method(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.todo), "Implement error handling (HIGH)")

    # Testing model properties
    def test_is_overdue_property(self):
        """Test the is_overdue property."""
        # By default, there's no due date so it can't be overdue
        self.assertFalse(self.todo.is_overdue)

        # Set a due date in the past
        past_date = timezone.now() - timedelta(days=1)
        self.todo.due_at = past_date
        self.todo.save()
        self.assertTrue(self.todo.is_overdue)

        # Set a due date in the future
        future_date = timezone.now() + timedelta(days=1)
        self.todo.due_at = future_date
        self.todo.save()
        self.assertFalse(self.todo.is_overdue)

    def test_days_until_due_property(self):
        """Test the days_until_due property."""
        # By default, there's no due date
        self.assertIsNone(self.todo.days_until_due)

        # Set a due date 3 days in the future
        # Use date with timezone to avoid time differences affecting the day calculation
        now = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        future_date = now + timedelta(days=3)
        self.todo.due_at = future_date
        self.todo.save()

        # Mock the timezone.now() call in the property to use our fixed time
        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.todo.days_until_due, 3)

        # Set a due date in the past
        past_date = now - timedelta(days=2)
        self.todo.due_at = past_date
        self.todo.save()

        # Mock the timezone.now() call in the property to use our fixed time
        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.todo.days_until_due, -2)

    def test_time_remaining_display_property(self):
        """Test the time_remaining_display property."""
        # No due date
        self.assertEqual(self.todo.time_remaining_display, "No due date")

        # Create a fixed reference time to avoid test failures due to time passing
        now = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)

        # Due date in future
        future_date = now + timedelta(days=5)
        self.todo.due_at = future_date
        self.todo.save()

        # Mock timezone.now to return our fixed time
        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.todo.time_remaining_display, "5 days remaining")

        # Due tomorrow
        tomorrow = now + timedelta(days=1)
        self.todo.due_at = tomorrow
        self.todo.save()

        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.todo.time_remaining_display, "1 day remaining")

        # Due today
        today = now + timedelta(hours=6)
        self.todo.due_at = today
        self.todo.save()

        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.todo.time_remaining_display, "Due today")

        # Overdue by 3 days
        past_date = now - timedelta(days=3)
        self.todo.due_at = past_date
        self.todo.save()

        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.todo.time_remaining_display, "Overdue by 3 days")

        # Overdue by 1 day
        yesterday = now - timedelta(days=1)
        self.todo.due_at = yesterday
        self.todo.save()

        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.todo.time_remaining_display, "Overdue by 1 day")

    # Testing methods
    def test_complete_method(self):
        """Test the complete method."""
        self.assertEqual(self.todo.status, "TODO")
        self.assertIsNone(self.todo.completed_at)

        self.todo.complete()
        self.assertEqual(self.todo.status, "DONE")
        self.assertIsNotNone(self.todo.completed_at)
        self.assertTrue(self.todo.is_completed)

    def test_reopen_method(self):
        """Test the reopen method."""
        # First complete it
        self.todo.complete()
        self.assertEqual(self.todo.status, "DONE")
        self.assertIsNotNone(self.todo.completed_at)

        # Then reopen it
        self.todo.reopen()
        self.assertEqual(self.todo.status, "TODO")
        self.assertIsNone(self.todo.completed_at)
        self.assertFalse(self.todo.is_completed)

    def test_set_priority_method(self):
        """Test the set_priority method."""
        self.assertEqual(self.todo.priority, "HIGH")

        self.todo.set_priority("LOW")
        self.assertEqual(self.todo.priority, "LOW")

        # Test with invalid priority
        with self.assertRaises(ValueError):
            self.todo.set_priority("INVALID")

    def test_set_status_method(self):
        """Test the set_status method."""
        self.assertEqual(self.todo.status, "TODO")

        self.todo.set_status("IN_PROGRESS")
        self.assertEqual(self.todo.status, "IN_PROGRESS")
        self.assertIsNone(self.todo.completed_at)

        self.todo.set_status("DONE")
        self.assertEqual(self.todo.status, "DONE")
        self.assertIsNotNone(self.todo.completed_at)

        # Test with invalid status
        with self.assertRaises(ValueError):
            self.todo.set_status("INVALID")

    # Testing Timestampable behavior
    def test_timestampable_behavior(self):
        """Test the timestampable behavior."""
        self.assertIsNotNone(self.todo.created_at)
        self.assertIsNotNone(self.todo.modified_at)

        old_modified = self.todo.modified_at
        self.todo.title = "Updated Title"
        self.todo.save()
        self.assertGreater(self.todo.modified_at, old_modified)
