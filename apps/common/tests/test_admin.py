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
    
    def test_team_admin(self):
        """Test the Team admin list view."""
        url = reverse('admin:common_team_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Team')
    
    def test_team_admin_add(self):
        """Test the Team admin add view."""
        url = reverse('admin:common_team_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name')
        self.assertContains(response, 'slug')
        self.assertContains(response, 'description')
        self.assertContains(response, 'is_active')
    
    def test_team_member_admin(self):
        """Test the TeamMember admin list view."""
        url = reverse('admin:common_teammember_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Check for presence of key elements rather than specific content
        self.assertContains(response, 'Team members')
        self.assertContains(response, 'Select team member to change')
    
    def test_team_member_inline(self):
        """Test the TeamMember inline in Team admin."""
        url = reverse('admin:common_team_change', args=[self.team.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Check for presence of inline section
        self.assertContains(response, 'Team members')
        self.assertContains(response, 'Add another Team member')