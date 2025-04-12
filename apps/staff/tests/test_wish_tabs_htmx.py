import pytest
from django.urls import reverse
from django.test import Client

from apps.common.tests.factories import UserFactory


class TestWishTabsHTMX:
    """Test for the wish list tab navigation with HTMX."""

    @pytest.fixture
    def client(self):
        """Set up a client with a logged-in staff user."""
        client = Client()
        user = UserFactory(is_staff=True)
        client.force_login(user)
        return client

    def test_tabs_htmx_response(self, client):
        """Test that tabs return HTMX content when requested."""
        # Test HTMX request for All tab
        response = client.get(
            reverse("staff:wish-list"),
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="wish-content-container",
        )
        assert response.status_code == 200

        # Should return just the content, not the full page
        content = response.content.decode()
        assert '<div id="wish-content-container">' in content
        assert '<div id="wish-tabs"' not in content

        # Test HTMX request for Draft tab
        response = client.get(
            reverse("staff:wish-list") + "?status=DRAFT",
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="wish-content-container",
        )
        assert response.status_code == 200

        # Should return just the content, not the full page
        content = response.content.decode()
        assert '<div id="wish-content-container">' in content
        assert '<div id="wish-tabs"' not in content

    def test_full_page_request(self, client):
        """Test that a regular request returns the full page."""
        # Test regular request
        response = client.get(reverse("staff:wish-list"))
        assert response.status_code == 200

        # Should return the full page with tabs
        content = response.content.decode()
        assert '<div id="wish-content-container">' in content
        assert '<div id="wish-tabs"' in content

        # Check that active tab is set correctly (should be All by default)
        assert 'tab-active">All</a>' in content

        # Test regular request with status filter
        response = client.get(reverse("staff:wish-list") + "?status=DRAFT")
        assert response.status_code == 200

        # Should return the full page with tabs
        content = response.content.decode()
        assert 'tab-active">Draft</a>' in content
