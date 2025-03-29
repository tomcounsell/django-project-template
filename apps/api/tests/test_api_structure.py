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
        
    def test_api_root_configured(self):
        """Test that the API root endpoint is configured"""
        url = "/api/"  # API root URL
        response = self.client.get(url)
        
        # API requires authentication, 
        # so we should get a 403 forbidden or 401 unauthorized
        self.assertIn(response.status_code, 
                     [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
        
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
        """Test that router URLs are properly included in the main urlconf"""
        # This test verifies that the router URLs are properly included
        # But since authentication is required, check for 403/401 response
        response = self.client.get('/api/')
        self.assertIn(response.status_code, 
                     [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
                
    def test_api_url_structure(self):
        """Test that the API has a proper URL structure"""
        # In this template, all URLs are under the /api/ prefix
        
        # Check URL pattern exists (even though authentication is required)
        url = "/api/"
        response = self.client.get(url)
        self.assertIn(response.status_code, 
                     [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])
    
    def test_swagger_json_accessible(self):
        """Test that OpenAPI schema JSON is accessible"""
        # With SWAGGER_USE_COMPAT_RENDERERS=False, the format is part of the query string
        response = self.client.get('/api/swagger/?format=json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the response is valid JSON with OpenAPI structure
        self.assertIn('application/json', response['Content-Type'])
        self.assertIn('swagger', response.json())
        self.assertIn('info', response.json())
        self.assertIn('paths', response.json())
        
    def test_api_docs_endpoints_configured(self):
        """Test that API documentation endpoints are configured in urls.py"""
        from django.urls import get_resolver
        
        # Get all URL patterns
        resolver = get_resolver()
        url_patterns = resolver.url_patterns
        
        # Check for Swagger/ReDoc URL patterns
        swagger_ui_found = False
        swagger_json_found = False
        redoc_found = False
        
        # Check URL patterns recursively
        def check_patterns(patterns):
            nonlocal swagger_ui_found, swagger_json_found, redoc_found
            for pattern in patterns:
                if hasattr(pattern, 'url_patterns'):
                    # This is an include, check its patterns
                    check_patterns(pattern.url_patterns)
                else:
                    # Check for swagger/redoc patterns by name
                    if hasattr(pattern, 'name'):
                        if pattern.name == 'schema-swagger-ui':
                            swagger_ui_found = True
                        elif pattern.name == 'schema-json':
                            swagger_json_found = True
                        elif pattern.name == 'schema-redoc':
                            redoc_found = True
        
        check_patterns(url_patterns)
        self.assertTrue(swagger_ui_found, "Swagger UI URL configuration not found")
        self.assertTrue(swagger_json_found, "Swagger JSON URL configuration not found")
        self.assertTrue(redoc_found, "ReDoc URL configuration not found")