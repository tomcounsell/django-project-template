from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import serializers, viewsets, status
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import get_user_model
from django.test import override_settings

# Create a simple model serializer for testing
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']

# Create a viewset for testing
class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)


class SimpleAPITestCase(APITestCase):
    """Simple API test that doesn't rely on the actual API implementation"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a test user
        cls.user = get_user_model().objects.create_user(
            username="test_api_user",
            email="test@example.com",
            password="password"
        )

    def setUp(self):
        self.client = APIClient()

    def test_api_client_setup(self):
        """Test that the API client is properly set up"""
        self.assertIsInstance(self.client, APIClient)

    def test_model_serializer(self):
        """Test that a simple model serializer works"""
        serializer = UserSerializer(instance=self.user)
        data = serializer.data
        
        # Check that the serializer includes expected fields
        self.assertIn('id', data)
        self.assertIn('username', data)
        self.assertIn('email', data)
        
        # Check field values
        self.assertEqual(data['username'], 'test_api_user')
        self.assertEqual(data['email'], 'test@example.com')

    def test_viewset_queryset(self):
        """Test that a viewset can access the model queryset"""
        viewset = UserViewSet()
        queryset = viewset.get_queryset()
        
        # Check that the queryset contains at least our test user
        self.assertGreaterEqual(queryset.count(), 1)
        self.assertIn(self.user, queryset)

    @override_settings(ROOT_URLCONF=__name__)
    def test_router_urls(self):
        """Test that a router generates the expected URL patterns"""
        # Get URL patterns from router
        patterns = router.urls
        
        # Check that we have list and detail patterns
        pattern_names = [pattern.name for pattern in patterns]
        self.assertIn('user-list', pattern_names)
        self.assertIn('user-detail', pattern_names)


# Minimal URL patterns for this test module
urlpatterns = [
    path('api/', include(router.urls)),
]