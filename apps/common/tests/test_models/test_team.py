"""
Tests for the Team model and related functionality.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from ..factories import UserFactory

User = get_user_model()


class TeamModelTestCase(TestCase):
    """Test cases for the Team model."""

    def setUp(self):
        """Set up test data."""
        self.user1 = UserFactory.create()
        self.user2 = UserFactory.create()
        self.user3 = UserFactory.create()

    def test_team_creation(self):
        """Test that a team can be created with valid data."""
        from apps.common.models.team import Team
        
        team = Team.objects.create(
            name="Test Team",
            slug="test-team",
            description="A team for testing"
        )
        
        self.assertEqual(team.name, "Test Team")
        self.assertEqual(team.slug, "test-team")
        self.assertEqual(team.description, "A team for testing")
        self.assertFalse(team.is_active)  # Should default to False
        
    def test_team_unique_slug(self):
        """Test that team slugs must be unique."""
        from apps.common.models.team import Team
        
        Team.objects.create(
            name="Team One",
            slug="team-slug",
            description="First team"
        )
        
        with self.assertRaises(IntegrityError):
            Team.objects.create(
                name="Team Two",
                slug="team-slug",  # Same slug as first team
                description="Second team"
            )
            
    def test_team_members(self):
        """Test adding members to a team."""
        from apps.common.models.team import Team, TeamMember, Role
        
        team = Team.objects.create(
            name="Test Team",
            slug="test-team",
            description="A team for testing",
            is_active=True
        )
        
        # Add members with different roles
        TeamMember.objects.create(team=team, user=self.user1, role=Role.OWNER.value)
        TeamMember.objects.create(team=team, user=self.user2, role=Role.ADMIN.value)
        TeamMember.objects.create(team=team, user=self.user3, role=Role.MEMBER.value)
        
        # Check team members
        self.assertEqual(team.members.count(), 3)
        self.assertEqual(team.get_owners().count(), 1)
        self.assertEqual(team.get_admins().count(), 2)  # Owner and admin
        
        # Check roles
        owner = TeamMember.objects.get(team=team, user=self.user1)
        self.assertEqual(owner.role, Role.OWNER.value)
        self.assertTrue(owner.is_owner)
        
        admin = TeamMember.objects.get(team=team, user=self.user2)
        self.assertEqual(admin.role, Role.ADMIN.value)
        self.assertTrue(admin.is_admin)
        self.assertFalse(admin.is_owner)
        
        member = TeamMember.objects.get(team=team, user=self.user3)
        self.assertEqual(member.role, Role.MEMBER.value)
        self.assertFalse(member.is_admin)
        
    def test_user_teams(self):
        """Test retrieving teams for a user."""
        from apps.common.models.team import Team, TeamMember, Role
        
        team1 = Team.objects.create(name="Team 1", slug="team-1", is_active=True)
        team2 = Team.objects.create(name="Team 2", slug="team-2", is_active=True)
        team3 = Team.objects.create(name="Team 3", slug="team-3", is_active=True)
        
        # Add user1 to all teams with different roles
        TeamMember.objects.create(team=team1, user=self.user1, role=Role.OWNER.value)
        TeamMember.objects.create(team=team2, user=self.user1, role=Role.ADMIN.value)
        TeamMember.objects.create(team=team3, user=self.user1, role=Role.MEMBER.value)
        
        # Add user2 to team1 only
        TeamMember.objects.create(team=team1, user=self.user2, role=Role.MEMBER.value)
        
        # User1 should be in 3 teams
        self.assertEqual(self.user1.teams.count(), 3)
        
        # User1 should own 1 team
        owned_teams = Team.objects.filter(
            teammember__user=self.user1, 
            teammember__role=Role.OWNER.value
        )
        self.assertEqual(owned_teams.count(), 1)
        
        # User2 should be in 1 team
        self.assertEqual(self.user2.teams.count(), 1)
        
    def test_team_permissions(self):
        """Test team permission checking methods."""
        from apps.common.models.team import Team, TeamMember, Role
        
        team = Team.objects.create(
            name="Test Team",
            slug="test-team",
            is_active=True
        )
        
        TeamMember.objects.create(team=team, user=self.user1, role=Role.OWNER.value)
        TeamMember.objects.create(team=team, user=self.user2, role=Role.ADMIN.value)
        TeamMember.objects.create(team=team, user=self.user3, role=Role.MEMBER.value)
        
        # Permission checks
        self.assertTrue(team.user_is_member(self.user1))
        self.assertTrue(team.user_is_member(self.user2))
        self.assertTrue(team.user_is_member(self.user3))
        
        self.assertTrue(team.user_can_manage(self.user1))
        self.assertTrue(team.user_can_manage(self.user2))
        self.assertFalse(team.user_can_manage(self.user3))
        
        self.assertTrue(team.user_can_edit(self.user1))
        self.assertTrue(team.user_can_edit(self.user2))
        self.assertFalse(team.user_can_edit(self.user3))
        
        self.assertTrue(team.user_can_delete(self.user1))
        self.assertFalse(team.user_can_delete(self.user2))
        self.assertFalse(team.user_can_delete(self.user3))