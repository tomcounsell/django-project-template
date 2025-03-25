import os
import unittest
from django.conf import settings


class TemplateMigrationTestCase(unittest.TestCase):
    """Tests for verifying templates after migration to root directories."""

    def test_base_template_exists_in_root(self):
        """Verify _base.html exists in root templates directory."""
        base_path = os.path.join(
            settings.BASE_DIR, 'templates', '_base.html'
        )
        self.assertTrue(
            os.path.exists(base_path),
            "Base template not found in root templates directory"
        )

    def test_partial_template_exists_in_root(self):
        """Verify _partial.html exists in root templates directory."""
        partial_path = os.path.join(
            settings.BASE_DIR, 'templates', '_partial.html'
        )
        self.assertTrue(
            os.path.exists(partial_path),
            "Partial template not found in root templates directory"
        )

    def test_account_login_template_exists_in_root(self):
        """Verify account/login.html exists in root templates directory."""
        template_path = os.path.join(
            settings.BASE_DIR, 'templates', 'account', 'login.html'
        )
        self.assertTrue(
            os.path.exists(template_path),
            "Login template not found in root templates directory"
        )

    def test_home_page_template_exists_in_root(self):
        """Verify pages/home.html exists in root templates directory."""
        template_path = os.path.join(
            settings.BASE_DIR, 'templates', 'pages', 'home.html'
        )
        self.assertTrue(
            os.path.exists(template_path),
            "Home page template not found in root templates directory"
        )

    def test_navbar_template_exists_in_root(self):
        """Verify nav/navbar.html exists in root templates directory."""
        template_path = os.path.join(
            settings.BASE_DIR, 'templates', 'nav', 'navbar.html'
        )
        self.assertTrue(
            os.path.exists(template_path),
            "Navbar template not found in root templates directory"
        )

    def test_footer_template_exists_in_root(self):
        """Verify layout/footer.html exists in root templates directory."""
        template_path = os.path.join(
            settings.BASE_DIR, 'templates', 'layout', 'footer.html'
        )
        self.assertTrue(
            os.path.exists(template_path),
            "Footer template not found in root templates directory"
        )
