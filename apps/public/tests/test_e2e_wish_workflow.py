"""
E2E test for the Wish management feature.
This test demonstrates how to:
1. Create a staff user and login
2. Navigate to the wishes page
3. Open a modal form to create a new wish
4. Fill and submit the form
5. Verify the wish appears in the list
6. Mark the wish as complete
"""

import os
import pytest
import unittest
from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model

# Check if required packages are installed
try:
    import playwright.sync_api as pw

    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("playwright not installed. Install with: pip install playwright")
    print("Then run: playwright install")


@pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="playwright not installed")
@pytest.mark.django_db
class TestWishWorkflow(LiveServerTestCase):
    """Test creating and completing a wish using the web UI."""

    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
        super().setUpClass()

    def setUp(self):
        """Set up the test by creating a staff user."""
        self.User = get_user_model()
        self.username = f"testuser_{os.urandom(4).hex()}"
        self.password = "password123"
        self.user = self.User.objects.create_user(
            username=self.username,
            password=self.password,
            email="staff@example.com",
            is_staff=True,
        )

        # Initialize playwright with headless browser (faster for CI environments)
        self.pw = pw.sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(60000)
        self.page.set_default_navigation_timeout(60000)
        self.screenshot_dir = "test_screenshots/wishes"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def tearDown(self):
        """Clean up after the test."""
        if hasattr(self, "page"):
            self.page.close()
        if hasattr(self, "browser"):
            self.browser.close()
        if hasattr(self, "pw"):
            self.pw.stop()

    def test_create_wish_workflow(self):
        """Test creating a wish using the modal from the wish list page."""
        # Get the server URL
        server_url = self.live_server_url

        # Login
        self.page.goto(f"{server_url}/account/login")
        self.page.screenshot(path=f"{self.screenshot_dir}/01_login_page.png")

        # Fill in login form and submit
        self.page.fill("#id_username", self.username)
        self.page.fill("#id_password", self.password)
        self.page.click('button[type="submit"]')
        self.page.wait_for_load_state("networkidle")
        self.page.screenshot(path=f"{self.screenshot_dir}/02_after_login.png")

        # Navigate to wishes page
        self.page.goto(f"{server_url}/staff/wishes/")
        self.page.wait_for_load_state("networkidle")
        self.page.screenshot(path=f"{self.screenshot_dir}/03_wishes_page.png")

        # Click create wish button
        self.page.click('text="Create New Wish"')
        self.page.wait_for_selector("#create-wish-modal")
        self.page.screenshot(path=f"{self.screenshot_dir}/04_create_wish_modal.png")

        # Fill in wish form
        self.page.fill("input[name='title']", "Test Wish E2E")
        self.page.fill(
            "textarea[name='description']", "This is a test wish created by E2E test"
        )
        self.page.select_option("select[name='priority']", "HIGH")
        self.page.fill("input[name='tags']", "test, e2e, automated")
        self.page.screenshot(path=f"{self.screenshot_dir}/05_filled_wish_form.png")

        # Submit the form
        submit_button = self.page.locator("#create-wish-form button[type='submit']")
        submit_button.click()

        # Wait for page to reload
        self.page.wait_for_load_state("networkidle")
        self.page.screenshot(path=f"{self.screenshot_dir}/06_after_submission.png")

        # Verify the wish appears in the list
        assert "Test Wish E2E" in self.page.content()
        assert "High" in self.page.content()

        # Find and click the complete button for our wish
        complete_button = self.page.locator(
            "tr:has-text('Test Wish E2E') button:has-text('Done')"
        )
        complete_button.click()

        # Wait for HTMX to update the page
        self.page.wait_for_timeout(1000)
        self.page.screenshot(path=f"{self.screenshot_dir}/07_wish_marked_complete.png")

        # Verify the wish status has changed to Done
        status_cell = self.page.locator("tr:has-text('Test Wish E2E') td:nth-child(4)")
        assert "Done" in status_cell.inner_text()


if __name__ == "__main__":
    # Allow running test directly
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    django.setup()

    # Create a test suite and run it
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWishWorkflow)
    unittest.TextTestRunner(verbosity=2).run(suite)
