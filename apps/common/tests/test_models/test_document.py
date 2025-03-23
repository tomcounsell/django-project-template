from django.test import TestCase
from unittest import mock

from ..test_behaviors import TimestampableTest
from ...models import Document, Upload, PDF
from ...models.document import create, accepted_file_types


class DocumentTest(TimestampableTest, TestCase):
    model = Document
    
    def create_instance(self, **kwargs):
        default_kwargs = {
            'original': 'https://example.com/document.pdf',
            'meta_data': {
                'mime_type': 'application/pdf',
                'ext': 'pdf'
            }
        }
        default_kwargs.update(kwargs)
        return Document.objects.create(**default_kwargs)
    
    def test_inheritance_from_upload(self):
        """Test that Document inherits from Upload"""
        document = self.create_instance()
        self.assertIsInstance(document, Upload)
        
    def test_display_property_implementation(self):
        """Test that the display property is implemented in the base class"""
        document = self.create_instance()
        self.assertIsNone(document.display)
        
        
class PDFTest(TestCase):
    def test_display_property(self):
        """Test that the display property returns the correct value for PDF documents"""
        pdf = PDF.objects.create(
            original='https://example.com/document.pdf',
            meta_data={
                'mime_type': 'application/pdf',
                'ext': 'pdf'
            }
        )
        self.assertEqual(pdf.display, "PDF Document")
        
        
class DocumentCreateTest(TestCase):
    def test_create_with_pdf_extension(self):
        """Test create function with PDF extension"""
        document = create('pdf')
        self.assertIsInstance(document, Document)
        
    def test_create_with_invalid_extension(self):
        """Test create function with invalid extension raises ValueError"""
        with self.assertRaises(ValueError):
            create('invalid')
            
    def test_create_with_uppercase_extension(self):
        """Test create function with uppercase extension works correctly"""
        document = create('PDF')
        self.assertIsInstance(document, Document)
        
    def test_accepted_file_types(self):
        """Test that the accepted_file_types list contains the expected values"""
        expected_types = ["pdf", "doc", "docx", "rtf", "pages"]
        self.assertEqual(accepted_file_types, expected_types)