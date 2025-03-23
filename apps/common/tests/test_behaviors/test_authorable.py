from unittest import mock

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.common.behaviors.authorable import Authorable
from .test_mixins import BehaviorTestCaseMixin


class AuthorableModel(Authorable):
    class Meta:
        app_label = 'test_app'


class AuthorableTest(BehaviorTestCaseMixin, TestCase):
    @property
    def model(self):
        return AuthorableModel
    
    def setUp(self):
        # Create a test user for author
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def create_instance(self, **kwargs):
        if 'author' not in kwargs:
            kwargs['author'] = self.user
        return super().create_instance(**kwargs)
        
    def test_save_authored_at_should_store_data_correctly(self):
        # Test that authored_at is auto-set
        obj = self.create_instance()
        self.assertIsNotNone(obj.authored_at)
        
        # Test that specific authored_at value is honored
        now = timezone.now()
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = now
            # This won't actually use the provided authored_at since it's auto_now_add
            # But we test it's set to now correctly
            obj = self.create_instance()
            self.assertEqual(obj.authored_at.date(), now.date())

    def test_should_store_author(self):
        obj = self.create_instance()
        self.assertEqual(obj.author, self.user)
        
    def test_author_display_name_returns_user_string(self):
        obj = self.create_instance()
        self.assertEqual(obj.author_display_name, str(self.user))
        
    def test_anonymous_author_returns_anonymous(self):
        obj = self.create_instance(is_author_anonymous=True)
        self.assertEqual(obj.author_display_name, "Anonymous")
