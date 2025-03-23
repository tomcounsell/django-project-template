from unittest import mock

from django.test import TestCase

from apps.common.behaviors.locatable import Locatable
from apps.common.models.address import Address
from .test_mixins import BehaviorTestCaseMixin


class LocatableModel(Locatable):
    class Meta:
        app_label = 'test_app'


class LocatableTest(BehaviorTestCaseMixin, TestCase):
    @property
    def model(self):
        return LocatableModel
    
    def setUp(self):
        # Create an address for testing
        self.address = Address.objects.create(
            street_address="123 Test St",
            city="Test City",
            state="TS",
            postal_code="12345",
            country="Test Country"
        )
    
    def test_can_set_and_get_address(self):
        # Test that address can be set and retrieved
        obj = self.model.objects.create(address=self.address)
        self.assertEqual(obj.address, self.address)
    
    def test_can_set_and_get_coordinates(self):
        # Test that longitude and latitude can be set and retrieved
        obj = self.model.objects.create(longitude=123.456, latitude=78.90)
        self.assertEqual(obj.longitude, 123.456)
        self.assertEqual(obj.latitude, 78.90)
    
    def test_address_can_be_null(self):
        # Test that address can be null
        obj = self.model.objects.create()
        self.assertIsNone(obj.address)
    
    def test_coordinates_can_be_null(self):
        # Test that coordinates can be null
        obj = self.model.objects.create()
        self.assertIsNone(obj.longitude)
        self.assertIsNone(obj.latitude)
    
    def test_address_deletion_sets_null(self):
        # Test that deleting an address sets the reference to null
        obj = self.model.objects.create(address=self.address)
        self.assertEqual(obj.address, self.address)
        
        # Delete the address
        self.address.delete()
        
        # Refresh the object and check that address is now null
        obj.refresh_from_db()
        self.assertIsNone(obj.address)