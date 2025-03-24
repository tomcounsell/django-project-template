"""
Tests for the Upload model and related functionality.
"""
from unittest import mock

from django.test import TestCase

from ..test_behaviors import TimestampableTest
from ...models import Upload


class UploadModelTestCase(TimestampableTest, TestCase):
    """Test cases for the Upload model."""
    model = Upload
    
    def setUp(self):
        """Set up test data."""
        # Create an upload with minimal data
        self.upload_minimal = Upload.objects.create(
            original="https://example.com/file.txt",
            name="simple_file",
            meta_data={}  # Initialize with empty dict instead of None
        )
        
        # Create an image upload with metadata
        self.image_meta = {
            "mime_type": "image/jpeg",
            "type": "image",
            "ext": "jpg",
            "meta": {
                "width": 800,
                "height": 600,
            }
        }
        
        self.image_upload = Upload.objects.create(
            original="https://example.com/image.jpg",
            name="test_image",
            thumbnail="https://example.com/image_thumb.jpg",
            meta_data=self.image_meta
        )
        
        # Create a PDF upload with metadata
        self.pdf_meta = {
            "mime_type": "application/pdf",
            "type": "document",
            "ext": "pdf",
            "etc": "resume"
        }
        
        self.pdf_upload = Upload.objects.create(
            original="https://example.com/document.pdf",
            meta_data=self.pdf_meta
        )
    
    def test_file_type_with_mocked_mime(self):
        """Test the file_type property returns the correct mime type."""
        # For uploads with meta_data, it should use the mime_type from meta_data
        with mock.patch('apps.common.models.upload.guess_type') as mock_guess_type:
            mock_guess_type.return_value = ("image/jpeg", None)
            self.assertEqual(self.image_upload.file_type, "image/jpeg")
            
            # For uploads without meta_data mime_type, it should use guess_type
            mock_guess_type.return_value = ("text/plain", None)
            self.assertEqual(self.upload_minimal.file_type, "text/plain")
    
    def test_is_image_property(self):
        """Test the is_image property returns the correct value."""
        # Test with direct mock of property
        with mock.patch.object(Upload, 'file_type', new_callable=mock.PropertyMock) as mock_file_type:
            # Set the file_type to image/jpeg for testing
            mock_file_type.return_value = "image/jpeg"
            self.assertTrue(self.image_upload.is_image)
            
            # Set the file_type to something non-image
            mock_file_type.return_value = "application/pdf"
            self.assertFalse(self.pdf_upload.is_image)
    
    def test_is_pdf_property(self):
        """Test the is_pdf property returns the correct value."""
        # Test with direct mock of property
        with mock.patch.object(Upload, 'file_type', new_callable=mock.PropertyMock) as mock_file_type:
            # Set the file_type to application/pdf for testing
            mock_file_type.return_value = "application/pdf"
            self.assertTrue(self.pdf_upload.is_pdf)
            
            # Set the file_type to something non-pdf
            mock_file_type.return_value = "image/jpeg"
            self.assertFalse(self.image_upload.is_pdf)
    
    def test_width_height_properties(self):
        """Test the width and height properties return the correct values."""
        # For image uploads with meta data
        with mock.patch.object(Upload, 'is_image', new_callable=mock.PropertyMock) as mock_is_image:
            mock_is_image.return_value = True
            self.assertEqual(self.image_upload.width, 800)
            self.assertEqual(self.image_upload.height, 600)
            
            # For uploads without image meta data
            self.assertIsNone(self.upload_minimal.width)
            self.assertIsNone(self.upload_minimal.height)
    
    def test_file_extension_property(self):
        """Test the file_extension property returns the correct value."""
        self.assertEqual(self.image_upload.file_extension, "jpg")
        self.assertEqual(self.pdf_upload.file_extension, "pdf")
        self.assertEqual(self.upload_minimal.file_extension, "")  # Empty dict
    
    def test_dimensions_property(self):
        """Test the dimensions property returns the correct values."""
        # Test with is_image mocked
        with mock.patch.object(Upload, 'is_image', new_callable=mock.PropertyMock) as mock_is_image:
            # Test with is_image True
            mock_is_image.return_value = True
            
            # For uploads with meta data
            self.assertEqual(self.image_upload.dimensions, (800, 600))
            
            # For uploads without meta_data
            self.assertEqual(self.upload_minimal.dimensions, (None, None))
    
    def test_link_title_property(self):
        """Test the link_title property returns the correct value."""
        # When name is present
        self.assertEqual(self.image_upload.link_title, "test_image .JPG")
        
        # When name is not present but etc is present
        test_pdf = Upload.objects.create(
            original="https://example.com/test.pdf",
            meta_data={"etc": "resume", "ext": "pdf"}
        )
        self.assertEqual(test_pdf.link_title, "RESUME .PDF")
        
        # Create an upload with type but no name or etc
        type_only_meta = {
            "type": "spreadsheet",
            "ext": "xlsx"
        }
        type_only_upload = Upload.objects.create(
            original="https://example.com/data.xlsx",
            meta_data=type_only_meta
        )
        self.assertEqual(type_only_upload.link_title, "SPREADSHEET .XLSX")
        
        # For uploads without any relevant meta_data
        minimal_meta = {"irrelevant": "data"}
        minimal_upload = Upload.objects.create(
            original="https://example.com/unknown",
            meta_data=minimal_meta
        )
        self.assertEqual(minimal_upload.link_title, "")
    
    def create_instance(self, **kwargs):
        """Create an Upload instance for testing."""
        if 'meta_data' not in kwargs:
            kwargs['meta_data'] = {}
        return Upload.objects.create(
            original="https://example.com/file.txt",
            **kwargs
        )