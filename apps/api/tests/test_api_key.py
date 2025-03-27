from django.urls import reverse
from rest_framework import status

from apps.api.tests.api_test_case import APITestCase
from apps.common.models import UserAPIKey, TeamAPIKey, Team, TeamMember


class APIKeyTestCase(APITestCase):
    """Test case for API key endpoints and authentication."""
    
    def setUp(self):
        super().setUp(create_app_user=True)
        # Create a team and make the user a member
        self.team = Team.objects.create(name='Test Team')
        self.team_member = TeamMember.objects.create(
            user=self.app_user,
            team=self.team,
            role='OWNER'
        )
        self.client.force_authenticate(user=self.app_user)
        
    def test_create_user_api_key(self):
        """Test creating a user API key."""
        url = reverse('api:user-api-key-list')
        data = {'name': 'Test API Key'}
        
        response = self.client.post(url, data, format='json')
        
        self.assert_staus_201_CREATED(response)
        self.assertIn('key', response.data)
        self.assertEqual(response.data['name'], 'Test API Key')
        self.assertEqual(UserAPIKey.objects.count(), 1)
        
    def test_list_user_api_keys(self):
        """Test listing user API keys."""
        # Create some API keys
        UserAPIKey.objects.create_key(name='Key 1', user=self.app_user)
        UserAPIKey.objects.create_key(name='Key 2', user=self.app_user)
        
        url = reverse('api:user-api-key-list')
        response = self.client.get(url)
        
        self.assert_staus_200_OK(response)
        self.assertEqual(len(response.data), 2)
        
    def test_revoke_user_api_key(self):
        """Test revoking a user API key."""
        api_key, _ = UserAPIKey.objects.create_key(name='Key to Revoke', user=self.app_user)
        
        url = reverse('api:user-api-key-revoke', kwargs={'pk': api_key.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Refresh from database
        api_key.refresh_from_db()
        self.assertTrue(api_key.revoked)
        
    def test_create_team_api_key(self):
        """Test creating a team API key."""
        url = reverse('api:team-api-key-list')
        data = {'name': 'Team API Key', 'team': self.team.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assert_staus_201_CREATED(response)
        self.assertIn('key', response.data)
        self.assertEqual(response.data['name'], 'Team API Key')
        self.assertEqual(TeamAPIKey.objects.count(), 1)
        
    def test_list_team_api_keys(self):
        """Test listing team API keys."""
        # Create some API keys
        TeamAPIKey.objects.create_key(name='Team Key 1', team=self.team)
        TeamAPIKey.objects.create_key(name='Team Key 2', team=self.team)
        
        url = reverse('api:team-api-key-list')
        response = self.client.get(url)
        
        self.assert_staus_200_OK(response)
        self.assertEqual(len(response.data), 2)
        
    def test_revoke_team_api_key(self):
        """Test revoking a team API key."""
        api_key, _ = TeamAPIKey.objects.create_key(name='Team Key to Revoke', team=self.team)
        
        url = reverse('api:team-api-key-revoke', kwargs={'pk': api_key.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Refresh from database
        api_key.refresh_from_db()
        self.assertTrue(api_key.revoked)
        
    def test_authentication_with_user_api_key(self):
        """Test authenticating with a user API key."""
        # Create API key for the user
        _, key = UserAPIKey.objects.create_key(name='Auth Test Key', user=self.app_user)
        
        # Create a todo item using the API key for authentication
        self.client.logout()  # Clear any session auth
        
        url = reverse('api:todoitem-list')
        data = {'title': 'Test Todo', 'description': 'Created with API Key'}
        
        # Use API key in header
        response = self.client.post(
            url, 
            data, 
            format='json',
            HTTP_X_API_KEY=key
        )
        
        self.assert_staus_201_CREATED(response)
        # Todo: Verify the todo was created with correct user