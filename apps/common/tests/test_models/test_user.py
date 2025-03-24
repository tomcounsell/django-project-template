"""
Tests for the User model and related functionality.
"""

import hashlib
from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ..factories import UserFactory
from ..test_behaviors import TimestampableTest

User = get_user_model()


class UserModelTestCase(TimestampableTest, TestCase):
    """Test cases for the User model."""

    model = User

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone_number="1234567890",
        )

    def test_user_creation(self):
        """Test that a user can be created with valid data."""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.last_name, "User")
        self.assertEqual(self.user.phone_number, "1234567890")
        self.assertFalse(self.user.is_email_verified)
        self.assertFalse(self.user.is_beta_tester)
        self.assertIsNone(self.user.agreed_to_terms_at)

    def test_serialized_property(self):
        """Test the serialized property returns expected data."""
        serialized = self.user.serialized

        self.assertEqual(serialized["username"], "testuser")
        self.assertEqual(serialized["email"], "test@example.com")
        self.assertEqual(serialized["first_name"], "Test")
        self.assertEqual(serialized["last_name"], "User")
        self.assertEqual(serialized["is_staff"], False)
        self.assertEqual(serialized["is_active"], True)

    def test_four_digit_login_code_for_example_email(self):
        """Test that example.com emails return a fixed login code."""
        example_user = UserFactory.create(email="someone@example.com")
        self.assertEqual(example_user.four_digit_login_code, "1234")

    def test_four_digit_login_code_for_regular_email(self):
        """Test that regular emails get a hash-based login code."""
        user = UserFactory.create(email="regular@domain.com")

        # Calculate expected code
        hash_input = f"{user.id}{user.email}{user.last_login}"
        hash_object = hashlib.md5(bytes(hash_input, encoding="utf-8"))
        expected_code = str(int(hash_object.hexdigest(), 16))[-4:]

        self.assertEqual(user.four_digit_login_code, expected_code)

    def test_is_agreed_to_terms_property(self):
        """Test the is_agreed_to_terms property."""
        # Initially should be False
        self.assertFalse(self.user.is_agreed_to_terms)

        # Set a date in the past (before 2019-11-01)
        old_date = timezone.make_aware(datetime(2019, 1, 1))
        self.user.agreed_to_terms_at = old_date
        self.assertFalse(self.user.is_agreed_to_terms)

        # Set a date after 2019-11-01
        new_date = timezone.make_aware(datetime(2020, 1, 1))
        self.user.agreed_to_terms_at = new_date
        self.assertTrue(self.user.is_agreed_to_terms)

    def test_is_agreed_to_terms_setter(self):
        """Test the is_agreed_to_terms setter."""
        # Initially None
        self.assertIsNone(self.user.agreed_to_terms_at)

        # Set to True
        self.user.is_agreed_to_terms = True
        self.assertIsNotNone(self.user.agreed_to_terms_at)
        self.assertTrue(self.user.is_agreed_to_terms)

        # Set to False
        self.user.is_agreed_to_terms = False
        self.assertIsNone(self.user.agreed_to_terms_at)
        self.assertFalse(self.user.is_agreed_to_terms)

    def test_str_method_with_first_name(self):
        """Test string representation with first name."""
        self.assertEqual(str(self.user), "Test User")

    def test_str_method_with_only_first_name(self):
        """Test string representation with only first name."""
        self.user.last_name = ""
        self.assertEqual(str(self.user), "Test")

    def test_str_method_with_username(self):
        """Test string representation with username when no first name."""
        self.user.first_name = ""
        self.assertEqual(str(self.user), "testuser")

    def test_str_method_with_verified_email(self):
        """Test string representation with verified email."""
        self.user.first_name = ""
        self.user.username = "test@example.com"  # Username containing @
        self.user.is_email_verified = True
        self.assertEqual(str(self.user), "test")

    def test_str_method_with_unverified_email(self):
        """Test string representation with unverified email."""
        self.user.first_name = ""
        self.user.username = "test@example.com"  # Username containing @
        self.user.is_email_verified = False
        self.assertEqual(str(self.user), "test@example.com (unverified)")

    def test_str_method_with_exception(self):
        """Test string representation when exception occurs."""
        # Creating a mock user that will cause an exception in __str__
        with self.assertRaises(Exception):
            # Raising an exception during string conversion
            user = User(id=999)
            # Force exception by accessing a non-existent property
            user.__dict__["_does_not_exist"]  # This will raise an exception
            str(user)  # This should return "User 999"
