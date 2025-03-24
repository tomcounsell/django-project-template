"""
Tests for the Django admin customizations.
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.common.models import Team, TeamMember, Role
from apps.common.tests.factories import UserFactory

# Override settings for testing
@override_settings(ALLOWED_HOSTS=['testserver'])
class AdminTestCase(TestCase):
    """Test cases for admin customizations."""
    
    def setUp(self):
        """Set up test data."""
        self.user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.client = Client()
        self.client.login(username='admin', password='password123')
        
        # Create team and members
        self.team = Team.objects.create(
            name="Test Team",
            slug="test-team",
            description="A team for testing",
            is_active=True
        )
        
        self.regular_user = UserFactory.create()
        self.team_member = TeamMember.objects.create(
            team=self.team,
            user=self.regular_user,
            role=Role.MEMBER.value
        )
    
    def test_admin_index(self):
        """Test the admin index page loads successfully."""
        url = '/admin/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Content Database')
    
    def test_unfold_integration(self):
        """Test that the admin site is using Django Unfold."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        # Get the admin site styles to check if our CSS is included
        self.assertIn("output.css", str(response.content))
    
    def test_admin_page(self):
        """Test the admin list page elements."""
        url = '/admin/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify that admin shows our custom page title
        self.assertContains(response, 'ProjectName Content Database')
        
        # Check for CSS output
        self.assertContains(response, 'output.css')
        
    def test_custom_dashboard(self):
        """Test the custom admin dashboard."""
        url = '/admin/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # The custom dashboard should contain summary cards
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Users Summary')
        self.assertContains(response, 'Teams Summary')
        
        # Check for specific dashboard elements
        self.assertContains(response, 'Recent Activity')