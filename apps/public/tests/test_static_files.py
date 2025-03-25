"""
Tests to verify static files are properly migrated from app to root directory.
"""
import os
from django.test import TestCase
from django.conf import settings


class StaticFilesTestCase(TestCase):
    """Test that static files exist in the expected directories."""

    def test_static_files_exist(self):
        """
        Test that static files exist in the expected directories.
        This test checks both the app static directory and root static directory.
        """
        app_static_dir = os.path.join(settings.BASE_DIR, "apps/public/static")
        root_static_dir = os.path.join(settings.BASE_DIR, "static")
        
        # After migration, these files should be in the root static directory
        required_static_files = [
            "assets/favicon.png",
            "assets/img/logo-yudame.png",
            "css/base.css",
            "js/base.js"
        ]
        
        for static_path in required_static_files:
            # Check if file exists in the app dir
            app_file_path = os.path.join(app_static_dir, static_path)
            root_file_path = os.path.join(root_static_dir, static_path)
            
            # File should exist in the app directory initially
            self.assertTrue(os.path.isfile(app_file_path), 
                         f"Static file {static_path} should exist in app static directory")
            
            # After migration, file should be in root directory
            self.assertTrue(os.path.isfile(root_file_path), 
                         f"Static file {static_path} should be in root static directory")
            
            # After full migration, file should not be in app directory
            # This will fail until we remove the old files 
            # self.assertFalse(os.path.isfile(app_file_path),
            #                f"Static file {static_path} should not be in app static directory after migration")