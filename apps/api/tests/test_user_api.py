import json
from rest_framework import status
from django.urls import reverse
from apps.api.tests.api_test_case import APITestCase
from apps.common.models import User


class UserAPITestCase(APITestCase):
    """Test suite for the User API endpoints"""

    def setUp(self):
        super().setUp()
        # Create test users with unique usernames
        self.admin_user = User.objects.create_superuser(
            username="test_admin_user",
            email="test_admin@example.com",
            password="adminpassword",
            is_email_verified=True
        )
        
        self.regular_user = User.objects.create_user(
            username="test_regular_user",
            email="test_user@example.com",
            password="userpassword",
            is_email_verified=True
        )
        
        self.unverified_user = User.objects.create_user(
            username="test_unverified_user",
            email="test_unverified@example.com",
            password="unverifiedpassword",
            is_email_verified=False
        )

    def test_list_users_as_admin(self):
        """Test that admin users can list all users"""
        # Login as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make request to list users
        response = self.client.get('/api/users/')
        
        # Check status code
        self.assert_staus_200_OK(response)
        
        # Check response contains all users
        self.assertEqual(len(response.data), 3)  # admin_user, regular_user, and unverified_user
        
        # Verify expected fields exist in response
        user_data = response.data[0]
        expected_fields = ["id", "username", "email", "first_name", "last_name", "is_staff"]
        self.assert_fields_exist(user_data, expected_fields)
        
        # Verify password is not in response
        self.assertNotIn("password", user_data)

    def test_list_users_as_regular_user(self):
        """Test that regular users can only see their own user data"""
        # Login as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Make request to list users
        response = self.client.get('/api/users/')
        
        # Check status code
        self.assert_staus_200_OK(response)
        
        # Check response contains only the authenticated user
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.regular_user.id))

    def test_retrieve_user_detail(self):
        """Test retrieving a specific user's details"""
        # Login as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Make request to get user details
        response = self.client.get(f'/api/users/{self.regular_user.id}/')
        
        # Check status code
        self.assert_staus_200_OK(response)
        
        # Verify user data
        self.assertEqual(response.data['id'], str(self.regular_user.id))
        self.assertEqual(response.data['username'], self.regular_user.username)
        self.assertEqual(response.data['email'], self.regular_user.email)

    def test_create_user(self):
        """Test creating a new user"""
        # Prepare user data
        new_user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "newuserpassword"
        }
        
        # Make request to create user
        response = self.client.post('/api/users/', new_user_data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user was created in database
        self.assertTrue(User.objects.filter(username="newuser").exists())
        
        # Check returned data
        self.assertEqual(response.data['username'], "newuser")
        self.assertEqual(response.data['email'], "newuser@example.com")
        self.assertEqual(response.data['first_name'], "New")
        self.assertEqual(response.data['last_name'], "User")
        
        # Verify password is not returned
        self.assertNotIn("password", response.data)

    def test_update_user(self):
        """Test updating a user's information"""
        # Login as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Prepare update data
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        
        # Make request to update user
        response = self.client.patch(f'/api/users/{self.regular_user.id}/', update_data, format='json')
        
        # Check status code
        self.assert_staus_200_OK(response)
        
        # Refresh user from database
        self.regular_user.refresh_from_db()
        
        # Verify user was updated
        self.assertEqual(self.regular_user.first_name, "Updated")
        self.assertEqual(self.regular_user.last_name, "Name")

    def test_user_cannot_update_other_user(self):
        """Test that a regular user cannot update another user's information"""
        # Login as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Prepare update data
        update_data = {
            "first_name": "Hacked",
            "last_name": "Name"
        }
        
        # Make request to update another user
        response = self.client.patch(f'/api/users/{self.admin_user.id}/', update_data, format='json')
        
        # This should fail with 404 (not found) because regular_user can't see admin_user
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Refresh admin user from database
        self.admin_user.refresh_from_db()
        
        # Verify admin user was not updated
        self.assertNotEqual(self.admin_user.first_name, "Hacked")