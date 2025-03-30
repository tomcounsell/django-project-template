# Behavior Mixins

This directory contains reusable model mixins that add specific behaviors to Django models. 
Each mixin provides attributes and methods that implement common functionality needed across different models.

## Available Behaviors

- **Annotatable**: Adds note functionality to a model
- **Authorable**: Adds author tracking with optional anonymity 
- **Expirable**: Adds functionality for content expiration
- **Locatable**: Adds location data with coordinates
- **Permalinkable**: Adds permalinking capability with slugs
- **Publishable**: Adds publishing workflow management
- **Timestampable**: Adds created/modified timestamps

## Usage

To use a behavior mixin, simply inherit from it in your model class:

```python
from django.db import models
from apps.common.behaviors.timestampable import Timestampable
from apps.common.behaviors.authorable import Authorable

class Article(Timestampable, Authorable, models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    
    # The model now has created_at, modified_at from Timestampable
    # and author, authored_at, is_author_anonymous from Authorable
```

## Testing

All behavior mixins are tested in `apps/common/tests/behaviors.py`, which contains:

1. **Database-backed tests**: Using Django's TestCase to test with ORM integration
2. **Direct tests**: Using Python's unittest with mocks to test without database

Both approaches provide comprehensive test coverage for all behaviors.

## Adding New Behaviors

To add a new behavior mixin:

1. Create a new file in this directory named after the behavior (e.g., `sortable.py`)
2. Implement the behavior as a mixin class
3. Add tests to `apps/common/tests/behaviors.py` 
4. Update this README to document the new behavior