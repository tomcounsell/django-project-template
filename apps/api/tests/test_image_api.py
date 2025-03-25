import uuid
from rest_framework import status
from apps.api.tests.api_test_case import APITestCase
from apps.common.models import User, Image


class ImageAPITestCase(APITestCase):
    """Test suite for the Image API endpoints"""

    def setUp(self):
        super().setUp()
        # Create test user with unique username
        self.user = User.objects.create_user(
            username="test_image_api_user",
            email="test_image_api@example.com",
            password="testpassword"
        )
        
        # Create test images
        self.image1 = Image.objects.create(
            author=self.user,
            url="https://example.com/image1.jpg",
            thumbnail_url="https://example.com/image1_thumb.jpg",
            meta_data={"width": 800, "height": 600, "format": "jpg"}
        )
        
        self.image2 = Image.objects.create(
            author=self.user,
            url="https://example.com/image2.jpg",
            thumbnail_url="https://example.com/image2_thumb.jpg",
            meta_data={"width": 1200, "height": 900, "format": "jpg"}
        )

    def test_list_images(self):
        """Test listing images"""
        # Login as the test user
        self.client.force_authenticate(user=self.user)
        
        # Make request to list images
        response = self.client.get('/api/images/')
        
        # Check status code
        self.assert_staus_200_OK(response)
        
        # Check response contains both images
        self.assertEqual(len(response.data), 2)
        
        # Verify expected fields exist in response
        image_data = response.data[0]
        expected_fields = ["id", "url", "thumbnail_url", "meta_data", "created_at", "modified_at"]
        self.assert_fields_exist(image_data, expected_fields)

    def test_retrieve_image_detail(self):
        """Test retrieving a specific image's details"""
        # Login as test user
        self.client.force_authenticate(user=self.user)
        
        # Make request to get image details
        response = self.client.get(f'/api/images/{self.image1.id}/')
        
        # Check status code
        self.assert_staus_200_OK(response)
        
        # Verify image data
        self.assertEqual(response.data['id'], str(self.image1.id))
        self.assertEqual(response.data['url'], self.image1.url)
        self.assertEqual(response.data['thumbnail_url'], self.image1.thumbnail_url)
        self.assertEqual(response.data['meta_data'], self.image1.meta_data)

    def test_create_image(self):
        """Test creating a new image"""
        # Login as test user
        self.client.force_authenticate(user=self.user)
        
        # Prepare image data
        new_image_data = {
            "url": "https://example.com/new_image.jpg",
            "thumbnail_url": "https://example.com/new_image_thumb.jpg",
            "meta_data": {"width": 1000, "height": 750, "format": "jpg"}
        }
        
        # Make request to create image
        response = self.client.post('/api/images/', new_image_data, format='json')
        
        # Check response
        self.assert_staus_201_CREATED(response)
        
        # Verify image was created in database
        self.assertTrue(Image.objects.filter(url="https://example.com/new_image.jpg").exists())
        
        # Verify author was set to the authenticated user
        image = Image.objects.get(url="https://example.com/new_image.jpg")
        self.assertEqual(image.author, self.user)

    def test_update_image(self):
        """Test updating an image"""
        # Login as test user
        self.client.force_authenticate(user=self.user)
        
        # Prepare update data
        update_data = {
            "meta_data": {"width": 800, "height": 600, "format": "jpg", "tags": ["landscape", "nature"]}
        }
        
        # Make request to update image
        response = self.client.patch(f'/api/images/{self.image1.id}/', update_data, format='json')
        
        # Check status code
        self.assert_staus_200_OK(response)
        
        # Refresh image from database
        self.image1.refresh_from_db()
        
        # Verify image was updated
        self.assertEqual(self.image1.meta_data.get("tags"), ["landscape", "nature"])

    def test_delete_image(self):
        """Test deleting an image"""
        # Login as test user
        self.client.force_authenticate(user=self.user)
        
        # Make request to delete image
        response = self.client.delete(f'/api/images/{self.image1.id}/')
        
        # Check status code
        self.assert_staus_204_DELETED(response)
        
        # Verify image was deleted from database
        self.assertFalse(Image.objects.filter(id=self.image1.id).exists())

    def test_unauthorized_access(self):
        """Test that unauthenticated requests are rejected"""
        # Make request without authentication
        response = self.client.get('/api/images/')
        
        # Check that request is rejected
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try to create an image without authentication
        new_image_data = {
            "url": "https://example.com/unauthorized_image.jpg",
            "thumbnail_url": "https://example.com/unauthorized_image_thumb.jpg",
            "meta_data": {"width": 1000, "height": 750, "format": "jpg"}
        }
        
        response = self.client.post('/api/images/', new_image_data, format='json')
        
        # Check that request is rejected
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify no image was created
        self.assertFalse(Image.objects.filter(url="https://example.com/unauthorized_image.jpg").exists())