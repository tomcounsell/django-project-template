"""
Test package for the common app.

This package contains tests for common app models, utilities, and behaviors.
Tests are organized into the following categories:

1. test_models/: Tests for individual model classes
2. test_behaviors/: Tests for behavior mixins using Django's TestCase
3. test_behaviors_direct.py: Standalone tests for behavior mixins without database
"""

# Import test classes for easy access
from apps.common.tests.test_behaviors import (
    AnnotatableTest,
    AuthorableTest,
    ExpirableTest,
    LocatableTest,
    PermalinkableTest,
    PublishableTest,
    TimestampableTest,
)