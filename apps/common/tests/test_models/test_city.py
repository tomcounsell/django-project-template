import uuid
from django.test import TestCase

from ...models import City, Country, Currency


class CityTest(TestCase):
    def setUp(self):
        self.currency = Currency.objects.create(
            code="USD",
            name="US Dollar",
            symbol="$"
        )
        
        self.country = Country.objects.create(
            name="United States",
            code="US",
            currency=self.currency
        )
    
    def test_city_creation(self):
        """Test basic city creation with required fields"""
        city = City.objects.create(
            name="New York",
            code="NYC",
            country=self.country
        )
        
        self.assertEqual(city.name, "New York")
        self.assertEqual(city.code, "nyc")  # should be lowercase due to signal
        self.assertEqual(city.country, self.country)
        self.assertIsInstance(city.id, uuid.UUID)
        
    def test_string_representation(self):
        """Test the string representation of a city"""
        city = City.objects.create(
            name="San Francisco",
            code="SFO",
            country=self.country
        )
        
        expected_str = "San Francisco, United States (sfo)"
        self.assertEqual(str(city), expected_str)
        
    def test_currency_property(self):
        """Test that the currency property returns the country's currency"""
        city = City.objects.create(
            name="Los Angeles",
            code="LAX",
            country=self.country
        )
        
        self.assertEqual(city.currency, self.currency)
        
    def test_lowercase_code_signal(self):
        """Test that the pre_save signal converts the code to lowercase"""
        city = City.objects.create(
            name="Chicago",
            code="ORD",
            country=self.country
        )
        
        self.assertEqual(city.code, "ord")
        
        # Test updating the code
        city.code = "CHI"
        city.save()
        
        # Refresh from database
        city.refresh_from_db()
        self.assertEqual(city.code, "chi")
        
    def test_verbose_name_plural(self):
        """Test that the verbose_name_plural is set correctly"""
        self.assertEqual(City._meta.verbose_name_plural, "cities")