from django.test import TestCase
from django.urls import reverse, resolve
from apps.api.urls import app_name, api_router
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status


class APIStructureTestCase(TestCase):
    """Tests for API URL structure and routing"""
    
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        
    def test_api_root_accessible(self):
        """Test that the API root endpoint is configured and accessible"""
        url = "/api/"  # API root URL
        response = self.client.get(url)
        
        # Should return 200 even without authentication for the root endpoint
        # (which typically shows available endpoints)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_api_namespacing(self):
        """Test that the API is properly namespaced"""
        self.assertEqual(app_name, "api")
        
    def test_router_configuration(self):
        """Test that the API router has essential endpoints registered"""
        # Get the registered URL patterns from the router
        url_patterns = api_router.urls
        
        # Extract URL pattern names
        url_names = [pattern.name for pattern in url_patterns if hasattr(pattern, 'name')]
        
        # Check for essential API endpoints
        expected_patterns = [
            'user-list',
            'user-detail',
        ]
        
        for pattern in expected_patterns:
            self.assertTrue(any(pattern in name for name in url_names), 
                           f"Expected pattern '{pattern}' not found in registered URLs")
            
    def test_router_urls_included(self):
        """Test that router URLs are included in the main urlconf"""
        # This test verifies that the router URLs are properly included
        # We'll check if we can access the API root
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
                
    def test_api_versioning(self):
        """Test that the API has proper versioning structure"""
        # In this template, all URLs are under the /api/ prefix
        # If versioning is implemented, would check for /api/v1/, etc.
        
        # Simple check that API root is accessible at expected path
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)