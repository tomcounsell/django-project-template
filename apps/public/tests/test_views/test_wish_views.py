from django.test import TestCase, override_settings
from django.urls import reverse

from apps.common.models import Wish
from apps.common.tests.factories import UserFactory, WishFactory


@override_settings(TESTING=True)
class WishViewsTestCase(TestCase):
    """Test case for Wish views."""

    def setUp(self):
        # Use a unique username to avoid conflicts with other tests
        import uuid

        self.username = f"wishuser_{uuid.uuid4().hex[:8]}"
        self.user = UserFactory.create(username=self.username, password="testpass123")

        # Create some test wish items
        self.wish1 = WishFactory.create(
            title="Complete project documentation",
            priority="HIGH",
            category="DOCUMENTATION",
            status="TODO",
            assignee=self.user,
        )

        self.wish2 = WishFactory.create(
            title="Fix API security issue",
            priority="HIGH",
            category="SECURITY",
            status="IN_PROGRESS",
            assignee=self.user,
        )

        self.wish3 = WishFactory.create(
            title="Optimize database queries",
            priority="MEDIUM",
            category="PERFORMANCE",
            status="TODO",
            assignee=None,
        )

        # URLs
        self.wish_list_url = reverse("public:wish-list")
        self.wish_create_url = reverse("public:wish-create")
        self.wish_detail_url = reverse(
            "public:wish-detail", kwargs={"pk": self.wish1.id}
        )
        self.wish_update_url = reverse(
            "public:wish-update", kwargs={"pk": self.wish1.id}
        )
        self.wish_delete_url = reverse(
            "public:wish-delete", kwargs={"pk": self.wish1.id}
        )
        self.wish_complete_url = reverse(
            "public:wish-complete", kwargs={"pk": self.wish1.id}
        )

        # Log in the user
        self.client.login(username=self.username, password="testpass123")

    def test_wish_list_view(self):
        """Test that the wish list view shows all wishes."""
        response = self.client.get(self.wish_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishes/wish_list.html")
        self.assertContains(response, "Complete project documentation")
        self.assertContains(response, "Fix API security issue")
        self.assertContains(response, "Optimize database queries")

        # Test filtering by status
        response = self.client.get(f"{self.wish_list_url}?status=TODO")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Complete project documentation")
        self.assertNotContains(response, "Fix API security issue")  # IN_PROGRESS
        self.assertContains(response, "Optimize database queries")

        # Test filtering by priority
        response = self.client.get(f"{self.wish_list_url}?priority=HIGH")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Complete project documentation")
        self.assertContains(response, "Fix API security issue")
        self.assertNotContains(response, "Optimize database queries")  # MEDIUM

        # Test filtering by assignee
        response = self.client.get(f"{self.wish_list_url}?assignee=me")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Complete project documentation")
        self.assertContains(response, "Fix API security issue")
        self.assertNotContains(response, "Optimize database queries")  # unassigned

    def test_wish_detail_view(self):
        """Test that the wish detail view shows the correct wish."""
        response = self.client.get(self.wish_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishes/wish_detail.html")
        self.assertContains(response, "Complete project documentation")
        self.assertContains(response, "HIGH")
        self.assertContains(response, "DOCUMENTATION")

    def test_wish_create_view(self):
        """Test creating a new wish."""
        # Test GET request
        response = self.client.get(self.wish_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishes/wish_form.html")

        # Test POST request with valid data
        wish_count_before = Wish.objects.count()
        response = self.client.post(
            self.wish_create_url,
            {
                "title": "New Wish Item",
                "description": "This is a new wish.",
                "priority": "LOW",
                "category": "GENERAL",
                "status": "TODO",
            },
            follow=True,
        )
        self.assertRedirects(response, self.wish_list_url)
        self.assertEqual(Wish.objects.count(), wish_count_before + 1)
        self.assertTrue(Wish.objects.filter(title="New Wish Item").exists())

        # Check that the new wish was assigned to the current user
        new_wish = Wish.objects.get(title="New Wish Item")
        self.assertEqual(new_wish.assignee, self.user)

    def test_wish_update_view(self):
        """Test updating an existing wish."""
        # Test GET request
        response = self.client.get(self.wish_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wishes/wish_form.html")
        self.assertContains(response, "Complete project documentation")

        # Test POST request with valid data
        response = self.client.post(
            self.wish_update_url,
            {
                "title": "Updated Wish Title",
                "description": "This is an updated wish.",
                "priority": "LOW",
                "category": "GENERAL",
                "status": "IN_PROGRESS",
                "assignee": self.user.id,
            },
            follow=True,
        )
        self.assertRedirects(
            response, reverse("public:wish-detail", kwargs={"pk": self.wish1.id})
        )
        self.wish1.refresh_from_db()
        self.assertEqual(self.wish1.title, "Updated Wish Title")
        self.assertEqual(self.wish1.description, "This is an updated wish.")
        self.assertEqual(self.wish1.priority, "LOW")
        self.assertEqual(self.wish1.status, "IN_PROGRESS")

    def test_wish_delete_view(self):
        """Test deleting a wish."""
        wish_count_before = Wish.objects.count()
        response = self.client.post(self.wish_delete_url, follow=True)
        self.assertEqual(Wish.objects.count(), wish_count_before - 1)
        self.assertFalse(Wish.objects.filter(id=self.wish1.id).exists())

    def test_wish_complete_view(self):
        """Test marking a wish as complete."""
        # Test marking as complete
        self.assertEqual(self.wish1.status, "TODO")
        response = self.client.post(self.wish_complete_url, follow=True)
        self.wish1.refresh_from_db()
        self.assertEqual(self.wish1.status, "DONE")
        self.assertIsNotNone(self.wish1.completed_at)

        # Test marking as incomplete
        response = self.client.post(
            f"{self.wish_complete_url}?mark_incomplete=true", follow=True
        )
        self.wish1.refresh_from_db()
        self.assertEqual(self.wish1.status, "TODO")
        self.assertIsNone(self.wish1.completed_at)

    def test_unauthenticated_access(self):
        """Test that unauthenticated users are redirected to login."""
        self.client.logout()

        response = self.client.get(self.wish_list_url)
        self.assertRedirects(response, f"/account/login?next={self.wish_list_url}")

        response = self.client.get(self.wish_detail_url)
        self.assertRedirects(response, f"/account/login?next={self.wish_detail_url}")

        response = self.client.get(self.wish_create_url)
        self.assertRedirects(response, f"/account/login?next={self.wish_create_url}")
