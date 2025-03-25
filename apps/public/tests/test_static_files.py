import os
import unittest
from django.conf import settings


class StaticFilesMigrationTestCase(unittest.TestCase):
    """Tests for verifying static files after migration to root dirs."""

    def test_css_files_exist_in_root(self):
        """Verify base.css exists in root static directory."""
        css_base_path = os.path.join(
            settings.BASE_DIR, 'static', 'css', 'base.css'
        )
        self.assertTrue(
            os.path.exists(css_base_path),
            "base.css not found in root static directory"
        )

    def test_js_files_exist_in_root(self):
        """Verify base.js exists in root static directory."""
        js_base_path = os.path.join(
            settings.BASE_DIR, 'static', 'js', 'base.js'
        )
        self.assertTrue(
            os.path.exists(js_base_path),
            "base.js not found in root static directory"
        )

    def test_favicon_exists_in_root(self):
        """Verify favicon.png exists in root static directory."""
        static_path = os.path.join(
            settings.BASE_DIR, 'static', 'assets', 'favicon.png'
        )
        self.assertTrue(
            os.path.exists(static_path),
            "favicon.png not found in root static directory"
        )

    def test_logo_exists_in_root(self):
        """Verify logo-yudame.png exists in root static directory."""
        static_path = os.path.join(
            settings.BASE_DIR, 'static', 'assets', 'img', 'logo-yudame.png'
        )
        self.assertTrue(
            os.path.exists(static_path),
            "logo-yudame.png not found in root static directory"
        )
