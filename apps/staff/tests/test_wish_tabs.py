import pytest
from django.urls import reverse
from django.test import Client

from apps.common.tests.factories import UserFactory


class TestWishTabsActiveState:
    """Test for the wish list tab navigation active states."""

    @pytest.fixture
    def client(self):
        """Set up a client with a logged-in staff user."""
        client = Client()
        user = UserFactory(is_staff=True)
        client.force_login(user)
        return client

    def test_all_tab_active_by_default(self, client):
        """Test that the 'All' tab is active by default with no filters."""
        response = client.get(reverse("staff:wish-list"))

        # Check for All tab active state
        assert (
            'class="border-slate-500 text-slate-700 font-medium'
            in response.content.decode()
        )
        assert ">All</a>" in response.content.decode()

    def test_status_tabs_activate_correctly(self, client):
        """Test that the correct tab is active when a status filter is applied."""
        # Test DRAFT tab
        response = client.get(reverse("staff:wish-list") + "?status=DRAFT")
        content = response.content.decode()
        assert "Draft</a>" in content
        assert 'class="border-slate-500 text-slate-700 font-medium' in content
        assert ">Draft<" in content and "border-slate-500" in content
        assert ">All<" in content and "border-transparent" in content

        # Test TODO tab
        response = client.get(reverse("staff:wish-list") + "?status=TODO")
        content = response.content.decode()
        assert 'class="border-slate-500 text-slate-700 font-medium' in content
        assert ">To Do<" in content and "border-slate-500" in content
        assert ">All<" in content and "border-transparent" in content

        # Test IN_PROGRESS tab
        response = client.get(reverse("staff:wish-list") + "?status=IN_PROGRESS")
        content = response.content.decode()
        assert 'class="border-slate-500 text-slate-700 font-medium' in content
        assert ">In Progress<" in content and "border-slate-500" in content
        assert ">All<" in content and "border-transparent" in content

    def test_combining_filters_preserves_status_tab(self, client):
        """Test that combining filters preserves the status tab selection."""
        # Test status with priority filter
        response = client.get(
            reverse("staff:wish-list") + "?status=DRAFT&priority=HIGH"
        )
        content = response.content.decode()

        # Check that DRAFT tab is still active
        assert ">Draft<" in content and "border-slate-500" in content
        assert ">All<" in content and "border-transparent" in content

        # Check that priority filter is included in other tab links
        assert "?status=TODO&priority=HIGH" in content
        assert "?status=IN_PROGRESS&priority=HIGH" in content
