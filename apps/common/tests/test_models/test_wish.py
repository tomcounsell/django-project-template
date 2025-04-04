import unittest.mock
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.common.models import User
from apps.common.tests.factories import UserFactory
from apps.staff.models import Wish


class WishModelTestCase(TestCase):
    """Test case for Wish model."""

    def setUp(self):
        self.user = UserFactory.create()
        self.wish = Wish.objects.create(
            title="Implement error handling",
            description="Add proper error handling to the API endpoints",
            priority="HIGH",
            category="API",
            assignee=self.user,
            status="TODO",
        )

    # Testing base fields
    def test_wish_creation(self):
        """Test that a wish can be created."""
        self.assertIsNotNone(self.wish.id)
        self.assertEqual(self.wish.title, "Implement error handling")
        self.assertEqual(
            self.wish.description, "Add proper error handling to the API endpoints"
        )
        self.assertEqual(self.wish.priority, "HIGH")
        self.assertEqual(self.wish.category, "API")
        self.assertEqual(self.wish.assignee, self.user)
        self.assertEqual(self.wish.status, "TODO")

    def test_wish_str_method(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.wish), "Implement error handling (HIGH)")

    # Testing model properties
    def test_is_overdue_property(self):
        """Test the is_overdue property."""
        # By default, there's no due date so it can't be overdue
        self.assertFalse(self.wish.is_overdue)

        # Set a due date in the past
        past_date = timezone.now() - timedelta(days=1)
        self.wish.due_at = past_date
        self.wish.save()
        self.assertTrue(self.wish.is_overdue)

        # Set a due date in the future
        future_date = timezone.now() + timedelta(days=1)
        self.wish.due_at = future_date
        self.wish.save()
        self.assertFalse(self.wish.is_overdue)

    def test_days_until_due_property(self):
        """Test the days_until_due property."""
        # By default, there's no due date
        self.assertIsNone(self.wish.days_until_due)

        # Set a due date 3 days in the future
        # Use date with timezone to avoid time differences affecting the day calculation
        now = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        future_date = now + timedelta(days=3)
        self.wish.due_at = future_date
        self.wish.save()

        # Mock the timezone.now() call in the property to use our fixed time
        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.wish.days_until_due, 3)

        # Set a due date in the past
        past_date = now - timedelta(days=2)
        self.wish.due_at = past_date
        self.wish.save()

        # Mock the timezone.now() call in the property to use our fixed time
        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.wish.days_until_due, -2)

    def test_time_remaining_display_property(self):
        """Test the time_remaining_display property."""
        # No due date
        self.assertEqual(self.wish.time_remaining_display, "No due date")

        # Create a fixed reference time to avoid test failures due to time passing
        now = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)

        # Due date in future
        future_date = now + timedelta(days=5)
        self.wish.due_at = future_date
        self.wish.save()

        # Mock timezone.now to return our fixed time
        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.wish.time_remaining_display, "5 days remaining")

        # Due tomorrow
        tomorrow = now + timedelta(days=1)
        self.wish.due_at = tomorrow
        self.wish.save()

        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.wish.time_remaining_display, "1 day remaining")

        # Due today
        today = now + timedelta(hours=6)
        self.wish.due_at = today
        self.wish.save()

        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.wish.time_remaining_display, "Due today")

        # Overdue by 3 days
        past_date = now - timedelta(days=3)
        self.wish.due_at = past_date
        self.wish.save()

        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.wish.time_remaining_display, "Overdue by 3 days")

        # Overdue by 1 day
        yesterday = now - timedelta(days=1)
        self.wish.due_at = yesterday
        self.wish.save()

        with unittest.mock.patch("django.utils.timezone.now", return_value=now):
            self.assertEqual(self.wish.time_remaining_display, "Overdue by 1 day")

    # Testing methods
    def test_complete_method(self):
        """Test the complete method."""
        self.assertEqual(self.wish.status, "TODO")
        self.assertIsNone(self.wish.completed_at)

        self.wish.complete()
        self.assertEqual(self.wish.status, "DONE")
        self.assertIsNotNone(self.wish.completed_at)
        self.assertTrue(self.wish.is_completed)

    def test_reopen_method(self):
        """Test the reopen method."""
        # First complete it
        self.wish.complete()
        self.assertEqual(self.wish.status, "DONE")
        self.assertIsNotNone(self.wish.completed_at)

        # Then reopen it
        self.wish.reopen()
        self.assertEqual(self.wish.status, "TODO")
        self.assertIsNone(self.wish.completed_at)
        self.assertFalse(self.wish.is_completed)

    def test_set_priority_method(self):
        """Test the set_priority method."""
        self.assertEqual(self.wish.priority, "HIGH")

        self.wish.set_priority("LOW")
        self.assertEqual(self.wish.priority, "LOW")

        # Test with invalid priority
        with self.assertRaises(ValueError):
            self.wish.set_priority("INVALID")

    def test_set_status_method(self):
        """Test the set_status method."""
        self.assertEqual(self.wish.status, "TODO")

        self.wish.set_status("IN_PROGRESS")
        self.assertEqual(self.wish.status, "IN_PROGRESS")
        self.assertIsNone(self.wish.completed_at)

        self.wish.set_status("DONE")
        self.assertEqual(self.wish.status, "DONE")
        self.assertIsNotNone(self.wish.completed_at)

        # Test with invalid status
        with self.assertRaises(ValueError):
            self.wish.set_status("INVALID")

    # Testing Timestampable behavior
    def test_timestampable_behavior(self):
        """Test the timestampable behavior."""
        self.assertIsNotNone(self.wish.created_at)
        self.assertIsNotNone(self.wish.modified_at)

        old_modified = self.wish.modified_at
        self.wish.title = "Updated Title"
        self.wish.save()
        self.assertGreater(self.wish.modified_at, old_modified)
