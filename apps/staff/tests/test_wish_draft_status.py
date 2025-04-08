"""
Tests for the DRAFT status feature in Wish model.
"""

import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.staff.models import Wish
from apps.common.forms.wish import WishForm


User = get_user_model()


class WishDraftStatusModelTestCase(TestCase):
    """Test the DRAFT status in the Wish model."""

    def test_draft_status_exists(self):
        """Test that DRAFT status exists in the model choices."""
        self.assertIn("DRAFT", dict(Wish.STATUS_CHOICES))
        self.assertEqual(dict(Wish.STATUS_CHOICES)["DRAFT"], "Draft")

    def test_default_status_is_draft(self):
        """Test that the default status for a new wish is DRAFT."""
        wish = Wish.objects.create(
            title="Test Default Status",
            description="This wish should have DRAFT as default status",
        )
        self.assertEqual(wish.status, "DRAFT")
        
    def test_set_status_method_accepts_draft(self):
        """Test that set_status method accepts DRAFT as a valid status."""
        wish = Wish.objects.create(
            title="Test Set Status",
            status="TODO"
        )
        wish.set_status("DRAFT")
        self.assertEqual(wish.status, "DRAFT")


class WishFormTestCase(TestCase):
    """Test the WishForm without status field for creation."""
    
    def test_form_excludes_status_field(self):
        """Test that the WishForm doesn't include the status field."""
        form = WishForm()
        self.assertNotIn('status', form.fields)
        
    def test_form_create_with_draft_status(self):
        """Test that a wish created with the form gets DRAFT status."""
        form_data = {
            'title': 'Form Created Wish',
            'description': 'This wish should get DRAFT status',
            'priority': 'MEDIUM',
            'tags': 'test, form',
        }
        form = WishForm(data=form_data)
        self.assertTrue(form.is_valid())
        wish = form.save(commit=False)
        # Status would be set by the view, let's simulate that
        wish.status = Wish.STATUS_DRAFT
        wish.save()
        saved_wish = Wish.objects.get(pk=wish.pk)
        self.assertEqual(saved_wish.status, "DRAFT")


@pytest.mark.django_db
class WishCreateViewTestCase(TestCase):
    """Test the Wish creation views to ensure they set DRAFT status."""

    def setUp(self):
        # Create a staff user
        self.user = User.objects.create_user(
            username="staffuser",
            password="testpassword",
            is_staff=True,
        )
        self.client = Client()
        self.client.login(username="staffuser", password="testpassword")
        
    def test_create_view_sets_draft_status(self):
        """Test that the create view sets DRAFT status."""
        url = reverse('staff:wish-create')
        data = {
            'title': 'Test Create View',
            'description': 'This wish should get DRAFT status',
            'priority': 'MEDIUM',
            'tags': 'test, view',
            'effort': 'sm',
            'value': '⭐️⭐️⭐️',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Check that the wish was created with DRAFT status
        wish = Wish.objects.get(title='Test Create View')
        self.assertEqual(wish.status, "DRAFT")
    
    def test_complete_view_can_change_draft_to_todo(self):
        """Test that the complete view can change a wish from DRAFT to TODO."""
        # Create a wish in DRAFT status
        wish = Wish.objects.create(
            title="Test Ready Button",
            description="This wish should move from DRAFT to TODO",
            status="DRAFT"
        )
        
        # Call the complete view to set status to TODO
        url = reverse('staff:wish-complete', kwargs={'pk': wish.pk})
        response = self.client.post(f"{url}?set_status=TODO", follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Refresh the wish from database
        wish.refresh_from_db()
        self.assertEqual(wish.status, "TODO")


@pytest.mark.django_db
class WishListViewTabsTestCase(TestCase):
    """Test the tabs functionality in the wish list view."""

    def setUp(self):
        # Create a staff user
        self.user = User.objects.create_user(
            username="staffuser",
            password="testpassword",
            is_staff=True,
        )
        self.client = Client()
        self.client.login(username="staffuser", password="testpassword")
        
        # Create wishes with different statuses
        self.draft_wish = Wish.objects.create(
            title="Draft Wish",
            status="DRAFT"
        )
        self.todo_wish = Wish.objects.create(
            title="Todo Wish",
            status="TODO"
        )
        self.in_progress_wish = Wish.objects.create(
            title="In Progress Wish",
            status="IN_PROGRESS"
        )
        self.done_wish = Wish.objects.create(
            title="Done Wish",
            status="DONE"
        )
        
    def test_list_view_has_tabs(self):
        """Test that the list view has tabs for different statuses."""
        url = reverse('staff:wish-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check that the tabs are present in the response
        content = response.content.decode('utf-8')
        self.assertIn('All', content)
        self.assertIn('Draft', content)
        self.assertIn('To Do', content)
        self.assertIn('In Progress', content)
        self.assertIn('Done', content)
        
    def test_filtering_by_tab(self):
        """Test that clicking on a tab filters wishes by status."""
        # Test Draft tab
        url = reverse('staff:wish-list') + '?status=DRAFT'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Draft Wish', content)
        self.assertNotIn('Todo Wish', content)
        
        # Test Todo tab
        url = reverse('staff:wish-list') + '?status=TODO'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Todo Wish', content)
        self.assertNotIn('Draft Wish', content)