"""
Factory classes for creating test models.

These factories allow for easy creation of model instances for testing.
Follows the Factory pattern to create models with sensible defaults
that can be overridden as needed.
"""

import random
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type, TypeVar

from django.contrib.auth import get_user_model
from django.db import models

from apps.common.models import Address, Country, Currency, Document, Image, Note, Upload

User = get_user_model()
T = TypeVar('T', bound=models.Model)


class ModelFactory:
    """Base factory class for creating model instances."""

    model_class: Type[models.Model]
    default_data: Dict[str, Any] = {}

    @classmethod
    def create(cls, **kwargs) -> T:
        """Create and save a model instance with given attributes."""
        data = cls.default_data.copy()
        data.update(kwargs)
        instance = cls.model_class(**data)
        instance.save()
        return instance

    @classmethod
    def build(cls, **kwargs) -> T:
        """Build a model instance without saving to database."""
        data = cls.default_data.copy()
        data.update(kwargs)
        return cls.model_class(**data)


class UserFactory(ModelFactory):
    """Factory for User model."""

    model_class = User
    default_data = {
        'username': lambda: f'user_{random.randint(1000, 9999)}',
        'email': lambda: f'user_{random.randint(1000, 9999)}@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'is_active': True,
    }

    @classmethod
    def create(cls, **kwargs) -> User:
        """Create a user with processed default values."""
        data = cls.default_data.copy()
        
        # Process any callable defaults
        for key, value in data.items():
            if callable(value):
                data[key] = value()
                
        data.update(kwargs)
        
        # Special handling for User model creation
        password = data.pop('password', 'testpassword123')
        user = User.objects.create_user(**data)
        user.set_password(password)
        user.save()
        return user


class CountryFactory(ModelFactory):
    """Factory for Country model."""

    model_class = Country
    default_data = {
        'name': 'United States',
        'code': 'US',
        'calling_code': '1',
    }


class AddressFactory(ModelFactory):
    """Factory for Address model."""

    model_class = Address
    default_data = {
        'line_1': '123 Test Street',
        'line_2': 'Apt 4B',
        'city': 'Test City',
        'state': 'TS',
        'postal_code': '12345',
        'country': None,  # Will be set in create method
    }

    @classmethod
    def create(cls, **kwargs) -> Address:
        """Create an address with a valid country if not specified."""
        data = cls.default_data.copy()
        data.update(kwargs)
        
        # Create a country if one isn't provided
        if not data.get('country'):
            data['country'] = CountryFactory.create()
            
        return super().create(**data)


class CurrencyFactory(ModelFactory):
    """Factory for Currency model."""

    model_class = Currency
    default_data = {
        'code': 'USD',
        'name': 'US Dollar',
        'symbol': '$',
    }


class NoteFactory(ModelFactory):
    """Factory for Note model."""

    model_class = Note
    default_data = {
        'text': 'This is a test note.',
        'author': None,  # Will be set in create method
    }

    @classmethod
    def create(cls, **kwargs) -> Note:
        """Create a note with a valid author if not specified."""
        data = cls.default_data.copy()
        data.update(kwargs)
        
        # Create an author if one isn't provided
        if not data.get('author'):
            data['author'] = UserFactory.create()
            
        return super().create(**data)


class UploadFactory(ModelFactory):
    """Factory for Upload model."""

    model_class = Upload
    default_data = {
        'original': 'https://example.com/test.jpg',
        'name': 'test.jpg',
        'type': 'image/jpeg',
        'size': 1024,
    }


class ImageFactory(ModelFactory):
    """Factory for Image model."""

    model_class = Image
    default_data = {
        'height': 600,
        'width': 800,
        'source_url': 'https://example.com/test.jpg',
    }


class DocumentFactory(ModelFactory):
    """Factory for Document model."""

    model_class = Document
    default_data = {
        'title': 'Test Document',
        'description': 'This is a test document.',
        'upload': None,  # Will be set in create method
    }

    @classmethod
    def create(cls, **kwargs) -> Document:
        """Create a document with a valid upload if not specified."""
        data = cls.default_data.copy()
        data.update(kwargs)
        
        # Create an upload if one isn't provided
        if not data.get('upload'):
            data['upload'] = UploadFactory.create()
            
        return super().create(**data)