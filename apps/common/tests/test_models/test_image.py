from django.test import TestCase
from unittest import mock

from ..test_behaviors import TimestampableTest
from ...models import Image, Upload


class ImageTest(TimestampableTest, TestCase):
    model = Image
    
    def create_instance(self, **kwargs):
        default_kwargs = {
            'original': 'https://example.com/image.jpg',
            'meta_data': {
                'mime_type': 'image/jpeg',
                'meta': {
                    'width': 800,
                    'height': 600
                }
            }
        }
        default_kwargs.update(kwargs)
        return Image.objects.create(**default_kwargs)
    
    def test_inheritance_from_upload(self):
        """Test that Image inherits from Upload"""
        image = self.create_instance()
        self.assertIsInstance(image, Upload)
        
    def test_thumbnail_url_field(self):
        """Test that thumbnail_url field is available"""
        image = self.create_instance(thumbnail_url='https://example.com/thumbnail.jpg')
        self.assertEqual(image.thumbnail_url, 'https://example.com/thumbnail.jpg')
        
    def test_width_property(self):
        """Test the width property returns the correct value from meta_data"""
        image = self.create_instance()
        self.assertEqual(image.width, 800)
        
        # Test with no meta field
        image_no_meta = self.create_instance(meta_data={'mime_type': 'image/jpeg'})
        self.assertIsNone(image_no_meta.width)
        
    def test_height_property(self):
        """Test the height property returns the correct value from meta_data"""
        image = self.create_instance()
        self.assertEqual(image.height, 600)
        
        # Test with no meta field
        image_no_meta = self.create_instance(meta_data={'mime_type': 'image/jpeg'})
        self.assertIsNone(image_no_meta.height)
        
    def test_is_image_property(self):
        """Test is_image property returns True for image files"""
        image = self.create_instance()
        self.assertTrue(image.is_image)
        
        # Test non-image file
        non_image = self.create_instance(meta_data={'mime_type': 'application/pdf'})
        self.assertFalse(non_image.is_image)