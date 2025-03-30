"""
Django TestCase-based tests for behavior mixins.

This package contains tests for behavior mixins using Django's TestCase
and actual database interactions. For standalone tests without database
dependencies, see the test_behaviors_direct.py file.
"""

from .test_annotatable import AnnotatableTest
from .test_authorable import AuthorableTest
from .test_expirable import ExpirableTest
from .test_locatable import LocatableTest
from .test_permalinkable import PermalinkableTest
from .test_publishable import PublishableTest
from .test_timestampable import TimestampableTest

__all__ = [
    'AnnotatableTest',
    'AuthorableTest', 
    'ExpirableTest',
    'LocatableTest',
    'PermalinkableTest',
    'PublishableTest',
    'TimestampableTest'
]
