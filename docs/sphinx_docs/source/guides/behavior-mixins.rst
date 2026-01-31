=============================
Behavior Mixins Guide
=============================

.. contents:: Table of Contents
   :local:
   :depth: 3

Introduction & Concept
======================

What are Behavior Mixins?
-------------------------

Behavior mixins are abstract Django model classes that encapsulate reusable functionality through Python's multiple inheritance. They provide a composable way to add common model features without code duplication or tight coupling.

A behavior mixin is simply an abstract Django model that:

- Defines fields, properties, and methods
- Uses ``Meta: abstract = True`` to prevent database table creation
- Can be combined with other mixins through multiple inheritance
- Follows Django's Method Resolution Order (MRO) for inheritance

**Example**: Instead of copying timestamp fields into every model:

.. code-block:: python

   # Without mixins - repetitive code
   class Article(models.Model):
       title = models.CharField(max_length=200)
       created_at = models.DateTimeField(auto_now_add=True)
       modified_at = models.DateTimeField(auto_now=True)

   class Product(models.Model):
       name = models.CharField(max_length=100)
       created_at = models.DateTimeField(auto_now_add=True)  # Duplicated!
       modified_at = models.DateTimeField(auto_now=True)     # Duplicated!

   # With mixins - DRY principle
   from apps.common.behaviors import Timestampable

   class Article(Timestampable, models.Model):
       title = models.CharField(max_length=200)

   class Product(Timestampable, models.Model):
       name = models.CharField(max_length=100)

Why Use Behavior Mixins?
-------------------------

**Benefits**:

1. **Code Reuse**: Write once, use everywhere. Common patterns become standardized.
2. **Maintainability**: Fix bugs or add features in one place, all models benefit.
3. **Readability**: Model definitions clearly show what behaviors they include.
4. **Flexibility**: Mix and match behaviors as needed for each model.
5. **Testing**: Test behaviors independently from business logic.
6. **Consistency**: Standardized field names and behavior across your codebase.

**Comparison to Alternatives**:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Approach
     - Pros
     - Cons
   * - **Copy-Paste Code**
     - Simple to understand
     - Massive duplication, hard to maintain, inconsistent naming
   * - **Abstract Base Models**
     - Similar benefits to mixins
     - Less flexible, single inheritance limits composition
   * - **Behavior Mixins**
     - Flexible, composable, testable
     - Requires understanding of MRO
   * - **Model Managers**
     - Good for querysets
     - Doesn't help with fields/properties
   * - **Proxy Models**
     - No schema changes
     - Limited to changing behavior, not adding fields

When to Use Behavior Mixins
----------------------------

**Use mixins when**:

- You need the same fields across multiple models (e.g., timestamps, author tracking)
- You want to enforce consistent patterns (e.g., publishing workflow)
- The behavior is truly generic and domain-agnostic
- You're building reusable components

**Avoid mixins when**:

- The fields are specific to one model or closely related models
- The behavior is complex and tightly coupled to business logic
- You're adding just one or two fields (overhead may not be worth it)
- The behavior needs to vary significantly across models

Comparison to Django's Built-in Options
----------------------------------------

**Django Abstract Models**: Behavior mixins are abstract models! The difference is organizational - mixins are designed for composition while abstract models often serve as base classes for related models.

**Django Proxy Models**: Proxy models change behavior without altering the database schema. Mixins add fields and behavior, requiring migrations.

**Model Managers**: Managers control querysets. Mixins add fields, properties, and instance methods. Often used together!

Quick Start Guide
=================

Installation
------------

Behavior mixins are already included in this Django project template. No additional installation is required.

The mixins are located in ``apps/common/behaviors/`` and can be imported as:

.. code-block:: python

   from apps.common.behaviors import (
       Timestampable,
       Authorable,
       Publishable,
       Expirable,
       Permalinkable,
       Locatable,
       Annotatable,
   )

Basic Usage Example
-------------------

Let's create a blog post model with multiple behaviors in under 5 minutes:

.. code-block:: python

   # apps/blog/models.py
   from django.db import models
   from apps.common.behaviors import Timestampable, Authorable, Publishable, Permalinkable

   class BlogPost(Timestampable, Authorable, Publishable, Permalinkable, models.Model):
       """A blog post with automatic timestamps, author tracking, publishing, and slug."""
       title = models.CharField(max_length=200)
       content = models.TextField()

       @property
       def slug_source(self):
           """Source field for automatic slug generation."""
           return self.title

       def __str__(self):
           return self.title

That's it! Your model now has:

- ``created_at`` and ``modified_at`` fields (Timestampable)
- ``author``, ``is_author_anonymous``, ``authored_at`` fields (Authorable)
- ``published_at``, ``edited_at``, ``unpublished_at`` fields and ``publish()``/``unpublish()`` methods (Publishable)
- ``slug`` field with automatic generation (Permalinkable)

**Using the model**:

.. code-block:: python

   from django.contrib.auth import get_user_model
   from apps.blog.models import BlogPost

   User = get_user_model()
   author = User.objects.first()

   # Create a new post
   post = BlogPost.objects.create(
       title="My First Post",
       content="Hello, world!",
       author=author
   )

   # Automatic fields are set
   print(f"Created: {post.created_at}")  # Auto-set
   print(f"Author: {post.author_display_name}")  # From Authorable
   print(f"Slug: {post.slug}")  # Auto-generated from title
   print(f"Published: {post.is_published}")  # False (not published yet)

   # Publish the post
   post.publish()
   post.save()
   print(f"Published: {post.is_published}")  # True
   print(f"Status: {post.publication_status}")  # "Published"

Common Patterns
---------------

**Pattern 1: Content Management**

Combine ``Timestampable``, ``Authorable``, ``Publishable``, and ``Permalinkable`` for content like blog posts, articles, or documentation:

.. code-block:: python

   class Article(Timestampable, Authorable, Publishable, Permalinkable, models.Model):
       title = models.CharField(max_length=200)
       content = models.TextField()

       @property
       def slug_source(self):
           return self.title

**Pattern 2: Time-Limited Resources**

Combine ``Timestampable`` and ``Expirable`` for coupons, tokens, or temporary access:

.. code-block:: python

   class Coupon(Timestampable, Expirable, models.Model):
       code = models.CharField(max_length=20, unique=True)
       discount_percent = models.IntegerField()

       def is_valid(self):
           """Check if coupon is valid (not expired)."""
           return not self.is_expired

**Pattern 3: Location-Based Services**

Combine ``Timestampable`` and ``Locatable`` for events, venues, or store locations:

.. code-block:: python

   class Event(Timestampable, Locatable, models.Model):
       name = models.CharField(max_length=200)
       start_time = models.DateTimeField()

       def distance_from(self, lat, lng):
           """Calculate distance from a given location."""
           if not self.has_coordinates:
               return None
           # Use GeoDjango or external library for distance calculation
           # ...

**Pattern 4: Annotated Content**

Combine ``Timestampable``, ``Authorable``, and ``Annotatable`` for internal tracking:

.. code-block:: python

   class SupportTicket(Timestampable, Authorable, Annotatable, models.Model):
       title = models.CharField(max_length=200)
       description = models.TextField()
       status = models.CharField(max_length=20)

       def add_internal_note(self, user, text):
           """Add an internal note to the ticket."""
           from apps.common.models import Note
           note = Note.objects.create(text=text, author=user)
           self.notes.add(note)

Individual Mixin Reference
==========================

Timestampable
-------------

**Purpose**: Automatically track when objects are created and modified.

**Module**: ``apps.common.behaviors.timestampable``

Fields Added
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field Name
     - Type
     - Description
   * - ``created_at``
     - DateTimeField
     - Timestamp when the object was created (set once, never changes)
   * - ``modified_at``
     - DateTimeField
     - Timestamp when the object was last modified (updates on every save)

Source Code
~~~~~~~~~~~

.. code-block:: python

   class Timestampable(models.Model):
       """
       An abstract mixin for models that need to track creation and modification timestamps.
       """
       created_at = models.DateTimeField(auto_now_add=True)
       modified_at = models.DateTimeField(auto_now=True)

       class Meta:
           abstract = True

Use Cases
~~~~~~~~~

1. **Audit Trails**: Track when records were created or changed
2. **Sorting by Recency**: Order by ``-created_at`` for newest-first
3. **Debugging**: Identify when problems started by checking modification times
4. **Data Analysis**: Analyze creation patterns over time
5. **Cache Invalidation**: Use ``modified_at`` to determine if cached data is stale

Code Examples
~~~~~~~~~~~~~

**Basic Usage**:

.. code-block:: python

   from django.db import models
   from apps.common.behaviors import Timestampable

   class Product(Timestampable, models.Model):
       name = models.CharField(max_length=100)
       price = models.DecimalField(max_digits=10, decimal_places=2)

   # Create a product
   product = Product.objects.create(name="Widget", price=9.99)
   print(f"Created: {product.created_at}")
   print(f"Modified: {product.modified_at}")

   # Update the product
   product.price = 12.99
   product.save()
   print(f"Modified: {product.modified_at}")  # Updated automatically

**Querying by Time Ranges**:

.. code-block:: python

   from django.utils import timezone
   from datetime import timedelta

   # Get products created in the last 7 days
   week_ago = timezone.now() - timedelta(days=7)
   recent_products = Product.objects.filter(created_at__gte=week_ago)

   # Get products modified today
   today = timezone.now().date()
   modified_today = Product.objects.filter(
       modified_at__date=today
   )

   # Get products never modified (created_at == modified_at)
   from django.db.models import F
   unmodified = Product.objects.filter(
       created_at__year=F('modified_at__year'),
       created_at__month=F('modified_at__month'),
       created_at__day=F('modified_at__day'),
       created_at__hour=F('modified_at__hour'),
       created_at__minute=F('modified_at__minute'),
   )

**Ordering by Timestamps**:

.. code-block:: python

   # Newest first
   products = Product.objects.order_by('-created_at')

   # Oldest first
   products = Product.objects.order_by('created_at')

   # Most recently modified
   products = Product.objects.order_by('-modified_at')

Gotchas and Important Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Bulk Updates Don't Trigger ``auto_now``**: The ``modified_at`` field won't update when using ``queryset.update()``:

   .. code-block:: python

      # This WILL update modified_at
      product.price = 15.99
      product.save()

      # This WON'T update modified_at
      Product.objects.filter(id=product.id).update(price=15.99)

      # Workaround: Update it manually
      from django.utils import timezone
      Product.objects.filter(id=product.id).update(
          price=15.99,
          modified_at=timezone.now()
      )

2. **Timestamps are Timezone-Aware**: By default, Django stores timestamps in UTC. Always use ``timezone.now()`` instead of ``datetime.now()``:

   .. code-block:: python

      from django.utils import timezone

      # Correct
      now = timezone.now()

      # Wrong (timezone-naive)
      from datetime import datetime
      now = datetime.now()  # Avoid this!

3. **Cannot Override on Create**: You cannot manually set ``created_at`` when creating an object:

   .. code-block:: python

      from django.utils import timezone
      from datetime import timedelta

      yesterday = timezone.now() - timedelta(days=1)

      # This will be ignored, created_at will be set to now()
      product = Product.objects.create(
          name="Widget",
          created_at=yesterday  # Ignored!
      )

4. **Microsecond Precision**: Timestamps include microseconds, which can cause comparison issues:

   .. code-block:: python

      # These might not be exactly equal due to microseconds
      before = timezone.now()
      product = Product.objects.create(name="Test")
      after = timezone.now()

      # This might fail
      assert product.created_at == before  # May differ by microseconds

      # Better: use ranges
      assert before <= product.created_at <= after

Authorable
----------

**Purpose**: Track content creators with support for anonymous authorship.

**Module**: ``apps.common.behaviors.authorable``

Fields Added
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field Name
     - Type
     - Description
   * - ``author``
     - ForeignKey(User)
     - The user who created the content (nullable, cascades on delete)
   * - ``is_author_anonymous``
     - BooleanField
     - Flag indicating whether the author should be kept anonymous
   * - ``authored_at``
     - DateTimeField
     - Timestamp when the content was authored (auto-set on creation)

Properties Added
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Property Name
     - Description
   * - ``author_display_name``
     - Returns "Anonymous" if ``is_author_anonymous`` is True, otherwise returns the string representation of the author

Source Code
~~~~~~~~~~~

.. code-block:: python

   from django.db import models
   from settings import AUTH_USER_MODEL

   class Authorable(models.Model):
       """A mixin for models that have an associated author."""
       author = models.ForeignKey(
           AUTH_USER_MODEL,
           related_name="%(class)ss",
           on_delete=models.CASCADE,
           null=True,
           blank=True,
       )
       is_author_anonymous = models.BooleanField(default=False)
       authored_at = models.DateTimeField(auto_now_add=True)

       @property
       def author_display_name(self):
           if self.is_author_anonymous:
               return "Anonymous"
           else:
               return str(self.author)

       class Meta:
           abstract = True

Use Cases
~~~~~~~~~

1. **User-Generated Content**: Track who created blog posts, comments, or reviews
2. **Audit Trails**: Know who created or modified records
3. **Attribution**: Display author names in UI
4. **Anonymous Posting**: Allow users to post anonymously while maintaining internal tracking
5. **Permission Checks**: Restrict editing to the original author

Code Examples
~~~~~~~~~~~~~

**Basic Usage**:

.. code-block:: python

   from django.db import models
   from django.contrib.auth import get_user_model
   from apps.common.behaviors import Authorable, Timestampable

   User = get_user_model()

   class Comment(Timestampable, Authorable, models.Model):
       text = models.TextField()
       post = models.ForeignKey('blog.BlogPost', on_delete=models.CASCADE)

   # Create a comment with an author
   user = User.objects.first()
   comment = Comment.objects.create(
       text="Great post!",
       author=user,
       post=some_post
   )

   print(comment.author_display_name)  # "John Doe"
   print(comment.authored_at)  # 2025-01-31 12:34:56

**Anonymous Content**:

.. code-block:: python

   # Create an anonymous comment
   comment = Comment.objects.create(
       text="Anonymous feedback",
       author=user,  # Still tracked internally
       is_author_anonymous=True,
       post=some_post
   )

   print(comment.author_display_name)  # "Anonymous"
   print(comment.author)  # <User: john> (still accessible)

**Querying by Author**:

.. code-block:: python

   # Get all comments by a specific user
   user_comments = Comment.objects.filter(author=user)

   # Get all non-anonymous comments
   public_comments = Comment.objects.filter(is_author_anonymous=False)

   # Get all anonymous comments
   anonymous_comments = Comment.objects.filter(is_author_anonymous=True)

   # Count posts per author
   from django.db.models import Count
   author_stats = Comment.objects.values('author__username').annotate(
       comment_count=Count('id')
   ).order_by('-comment_count')

**Permission Checks**:

.. code-block:: python

   class Comment(Timestampable, Authorable, models.Model):
       text = models.TextField()
       post = models.ForeignKey('blog.BlogPost', on_delete=models.CASCADE)

       def can_edit(self, user):
           """Check if a user can edit this comment."""
           return user == self.author or user.is_staff

       def can_delete(self, user):
           """Check if a user can delete this comment."""
           return user == self.author or user.is_staff

   # Usage
   if comment.can_edit(request.user):
       # Show edit button
       pass

Gotchas and Important Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Handling Deleted Users**: The ``author`` field uses ``on_delete=models.CASCADE``, meaning if a user is deleted, all their authored content is deleted too. Consider using ``SET_NULL`` instead:

   .. code-block:: python

      # Custom implementation with SET_NULL
      class Comment(models.Model):
          author = models.ForeignKey(
              AUTH_USER_MODEL,
              on_delete=models.SET_NULL,  # Keep content when user deleted
              null=True,
              blank=True,
          )
          # ... rest of Authorable fields

2. **Related Name Pattern**: The ``related_name="%(class)ss"`` creates a reverse relation like ``user.comments`` (lowercase model name + 's'). This can be customized:

   .. code-block:: python

      # Access all comments by a user
      user.comments.all()

      # If your model name is BlogPost, the relation is:
      user.blogposts.all()

3. **Anonymous vs No Author**: There's a difference between anonymous and having no author:

   .. code-block:: python

      # Anonymous: Has an author but displays as "Anonymous"
      comment1 = Comment(author=user, is_author_anonymous=True)
      print(comment1.author_display_name)  # "Anonymous"

      # No author: Author field is None
      comment2 = Comment(author=None)
      print(comment2.author_display_name)  # "None"

4. **Combining with Timestampable**: When combining with Timestampable, you get both ``authored_at`` and ``created_at``. They're usually the same but serve different purposes:

   .. code-block:: python

      class BlogPost(Timestampable, Authorable, models.Model):
          title = models.CharField(max_length=200)

      # authored_at: When content was authored (from Authorable)
      # created_at: When database record was created (from Timestampable)
      # Usually the same, but semantically different

Publishable
-----------

**Purpose**: Add a complete publishing workflow with draft, published, and unpublished states.

**Module**: ``apps.common.behaviors.publishable``

Fields Added
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field Name
     - Type
     - Description
   * - ``published_at``
     - DateTimeField
     - Timestamp when content was published (nullable)
   * - ``edited_at``
     - DateTimeField
     - Timestamp when content was last edited after publication (nullable)
   * - ``unpublished_at``
     - DateTimeField
     - Timestamp when content was unpublished (nullable)

Properties Added
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Property Name
     - Description
   * - ``is_published``
     - Boolean indicating if content is currently published (also a setter)
   * - ``publication_status``
     - Human-readable status: "Published", "Unpublished", or "Draft"

Methods Added
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Method Name
     - Description
   * - ``publish()``
     - Marks content as published by setting ``published_at`` to now
   * - ``unpublish()``
     - Marks content as unpublished by setting ``unpublished_at`` to now

Source Code
~~~~~~~~~~~

.. code-block:: python

   from django.db import models
   from django.utils import timezone

   class Publishable(models.Model):
       """A behavior mixin that adds publishing workflow functionality."""
       published_at = models.DateTimeField(null=True, blank=True)
       edited_at = models.DateTimeField(null=True, blank=True)
       unpublished_at = models.DateTimeField(null=True, blank=True)

       class Meta:
           abstract = True

       @property
       def is_published(self) -> bool:
           """Check if the content is currently published."""
           now = timezone.now()
           # If unpublished_at is more recent than published_at, item is unpublished
           if self.unpublished_at and (
               not self.published_at or self.unpublished_at > self.published_at
           ):
               return False
           # Item is published if it has a published_at date in the past
           elif self.published_at and self.published_at < now:
               return True
           else:
               return False

       @is_published.setter
       def is_published(self, value: bool):
           """Set the publication status."""
           if value and not self.is_published:
               self.unpublished_at = None
               self.published_at = timezone.now()
           elif not value and self.is_published:
               self.unpublished_at = timezone.now()

       def publish(self):
           """Publish the content."""
           self.is_published = True

       def unpublish(self):
           """Unpublish the content."""
           self.is_published = False

       @property
       def publication_status(self) -> str:
           """Get human-readable publication status."""
           if self.is_published:
               return "Published"
           elif self.published_at:
               return "Unpublished"
           else:
               return "Draft"

Use Cases
~~~~~~~~~

1. **Blog Posts**: Manage draft, publish, and unpublish blog posts
2. **Articles**: Control when content goes live
3. **Scheduled Publishing**: Set ``published_at`` to a future date for scheduled releases
4. **Content Review**: Keep content as drafts until approved
5. **Temporary Unpublishing**: Remove content temporarily (e.g., for updates)

Code Examples
~~~~~~~~~~~~~

**Basic Publishing Workflow**:

.. code-block:: python

   from django.db import models
   from apps.common.behaviors import Timestampable, Publishable

   class Article(Timestampable, Publishable, models.Model):
       title = models.CharField(max_length=200)
       content = models.TextField()

   # Create a draft article
   article = Article.objects.create(
       title="My Article",
       content="Article content..."
   )

   print(article.publication_status)  # "Draft"
   print(article.is_published)  # False

   # Publish the article
   article.publish()
   article.save()

   print(article.publication_status)  # "Published"
   print(article.is_published)  # True
   print(article.published_at)  # 2025-01-31 12:34:56

   # Unpublish the article
   article.unpublish()
   article.save()

   print(article.publication_status)  # "Unpublished"
   print(article.is_published)  # False

**Filtering Published Content**:

.. code-block:: python

   from django.utils import timezone

   # Get all published articles (manual filtering)
   published = Article.objects.filter(
       published_at__isnull=False,
       published_at__lte=timezone.now()
   ).exclude(
       unpublished_at__gt=models.F('published_at')
   )

   # Better: Create a custom manager
   class PublishedManager(models.Manager):
       def get_queryset(self):
           now = timezone.now()
           return super().get_queryset().filter(
               published_at__isnull=False,
               published_at__lte=now
           ).filter(
               models.Q(unpublished_at__isnull=True) |
               models.Q(unpublished_at__lt=models.F('published_at'))
           )

   class Article(Timestampable, Publishable, models.Model):
       title = models.CharField(max_length=200)
       content = models.TextField()

       objects = models.Manager()  # Default manager
       published = PublishedManager()  # Published-only manager

   # Usage
   all_articles = Article.objects.all()
   published_articles = Article.published.all()

**Scheduled Publishing**:

.. code-block:: python

   from django.utils import timezone
   from datetime import timedelta

   # Schedule article for tomorrow
   tomorrow = timezone.now() + timedelta(days=1)
   article = Article.objects.create(
       title="Future Article",
       content="This will be published tomorrow",
       published_at=tomorrow
   )

   print(article.is_published)  # False (not published yet)
   print(article.publication_status)  # "Unpublished"

   # After tomorrow, is_published will be True
   # You might use a cron job or Celery task to send notifications

**Admin Integration**:

.. code-block:: python

   from django.contrib import admin
   from django.utils.html import format_html

   @admin.register(Article)
   class ArticleAdmin(admin.ModelAdmin):
       list_display = ['title', 'status_badge', 'published_at']
       list_filter = ['publication_status']
       actions = ['publish_items', 'unpublish_items']

       def status_badge(self, obj):
           """Display a colored badge for publication status."""
           status = obj.publication_status
           colors = {
               'Published': 'green',
               'Draft': 'gray',
               'Unpublished': 'orange'
           }
           color = colors.get(status, 'gray')
           return format_html(
               '<span style="color: {};">{}</span>',
               color,
               status
           )
       status_badge.short_description = 'Status'

       def publish_items(self, request, queryset):
           """Bulk publish action."""
           for item in queryset:
               item.publish()
               item.save()
       publish_items.short_description = "Publish selected items"

       def unpublish_items(self, request, queryset):
           """Bulk unpublish action."""
           for item in queryset:
               item.unpublish()
               item.save()
       unpublish_items.short_description = "Unpublish selected items"

Gotchas and Important Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Timezone Handling**: Always use timezone-aware datetimes for ``published_at``:

   .. code-block:: python

      from django.utils import timezone

      # Correct
      article.published_at = timezone.now()

      # Wrong (timezone-naive)
      from datetime import datetime
      article.published_at = datetime.now()  # Avoid!

2. **Future Publishing**: Content with ``published_at`` in the future is not considered published:

   .. code-block:: python

      from datetime import timedelta

      # Schedule for tomorrow
      article.published_at = timezone.now() + timedelta(days=1)
      article.save()

      print(article.is_published)  # False (future date)

3. **Unpublish vs Delete**: Unpublishing preserves content while making it invisible. Consider your use case:

   .. code-block:: python

      # Unpublish: Content hidden but preserved
      article.unpublish()
      article.save()

      # Delete: Content removed
      article.delete()

4. **Manual ``published_at`` Settings**: If you manually set ``published_at``, remember to clear ``unpublished_at``:

   .. code-block:: python

      # Wrong: Might be considered unpublished
      article.published_at = timezone.now()
      # unpublished_at might still be set!

      # Right: Use the publish() method
      article.publish()
      article.save()

5. **Don't Forget to Save**: The ``publish()`` and ``unpublish()`` methods don't save automatically:

   .. code-block:: python

      # Wrong: Changes not persisted
      article.publish()

      # Right: Save after publishing
      article.publish()
      article.save()

Expirable
---------

**Purpose**: Add validity periods to content that can expire.

**Module**: ``apps.common.behaviors.expirable``

Fields Added
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field Name
     - Type
     - Description
   * - ``valid_at``
     - DateTimeField
     - Timestamp when content becomes valid (nullable)
   * - ``expired_at``
     - DateTimeField
     - Timestamp when content expires (nullable)

Properties Added
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Property Name
     - Description
   * - ``is_expired``
     - Boolean indicating if content has expired (also a setter)

Source Code
~~~~~~~~~~~

.. code-block:: python

   from django.db import models

   class Expirable(models.Model):
       """A mixin for models that require expiration functionality."""
       valid_at = models.DateTimeField(null=True, blank=True)
       expired_at = models.DateTimeField(null=True, blank=True)

       @property
       def is_expired(self) -> bool:
           from django.utils.timezone import now
           return True if self.expired_at and self.expired_at < now() else False

       @is_expired.setter
       def is_expired(self, value: bool):
           from django.utils.timezone import now
           if value is True:
               self.expired_at = now()
           elif value is False and self.is_expired:
               self.expired_at = None
           elif value is None:
               self.expired_at = None

       class Meta:
           abstract = True

Use Cases
~~~~~~~~~

1. **Coupons**: Set expiration dates for promotional codes
2. **Access Tokens**: Temporary API or authentication tokens
3. **Temporary Content**: Time-limited announcements or banners
4. **Subscriptions**: Track when subscriptions expire
5. **Limited-Time Offers**: Promotions valid for a specific period

Code Examples
~~~~~~~~~~~~~

**Basic Usage**:

.. code-block:: python

   from django.db import models
   from django.utils import timezone
   from datetime import timedelta
   from apps.common.behaviors import Timestampable, Expirable

   class Coupon(Timestampable, Expirable, models.Model):
       code = models.CharField(max_length=20, unique=True)
       discount_percent = models.IntegerField()

   # Create a coupon valid for 30 days
   coupon = Coupon.objects.create(
       code="SAVE20",
       discount_percent=20,
       expired_at=timezone.now() + timedelta(days=30)
   )

   print(coupon.is_expired)  # False

   # After 30 days, is_expired will be True
   print(coupon.expired_at)  # 2025-03-02 12:34:56

**Validity Windows**:

.. code-block:: python

   from django.utils import timezone
   from datetime import timedelta

   # Create a coupon valid from tomorrow for 7 days
   tomorrow = timezone.now() + timedelta(days=1)
   next_week = tomorrow + timedelta(days=7)

   coupon = Coupon.objects.create(
       code="WEEK20",
       discount_percent=20,
       valid_at=tomorrow,
       expired_at=next_week
   )

   # Check if currently valid
   def is_currently_valid(obj):
       now = timezone.now()
       if obj.is_expired:
           return False
       if obj.valid_at and obj.valid_at > now:
           return False  # Not valid yet
       return True

   print(is_currently_valid(coupon))  # False (not valid until tomorrow)

**Querying Active Items**:

.. code-block:: python

   from django.utils import timezone

   # Get all active (non-expired) coupons
   active_coupons = Coupon.objects.filter(
       models.Q(expired_at__isnull=True) | models.Q(expired_at__gt=timezone.now())
   )

   # Get all expired coupons
   expired_coupons = Coupon.objects.filter(
       expired_at__lte=timezone.now()
   )

   # Get coupons expiring in the next 7 days
   week_from_now = timezone.now() + timedelta(days=7)
   expiring_soon = Coupon.objects.filter(
       expired_at__gte=timezone.now(),
       expired_at__lte=week_from_now
   )

**Manual Expiration**:

.. code-block:: python

   # Manually expire a coupon
   coupon.is_expired = True
   coupon.save()

   print(coupon.is_expired)  # True
   print(coupon.expired_at)  # Current timestamp

   # Unexpire a coupon
   coupon.is_expired = False
   coupon.save()

   print(coupon.is_expired)  # False
   print(coupon.expired_at)  # None

**Custom Validation**:

.. code-block:: python

   class Coupon(Timestampable, Expirable, models.Model):
       code = models.CharField(max_length=20, unique=True)
       discount_percent = models.IntegerField()
       max_uses = models.IntegerField(default=100)
       uses_count = models.IntegerField(default=0)

       def is_valid(self):
           """Check if coupon is valid (not expired and has uses left)."""
           if self.is_expired:
               return False
           if self.uses_count >= self.max_uses:
               return False
           return True

       def use(self):
           """Use the coupon."""
           if not self.is_valid():
               raise ValueError("Coupon is not valid")
           self.uses_count += 1
           if self.uses_count >= self.max_uses:
               self.is_expired = True
           self.save()

Gotchas and Important Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Nullable Fields**: Both ``valid_at`` and ``expired_at`` are nullable. A None value has specific meaning:

   .. code-block:: python

      # Never expires
      coupon = Coupon(code="FOREVER", expired_at=None)
      print(coupon.is_expired)  # False

      # Valid immediately
      coupon = Coupon(code="NOW", valid_at=None)
      # No valid_at check in is_expired, handle separately

2. **``is_expired`` Only Checks Past**: The ``is_expired`` property only checks if content has expired. It doesn't check if content is valid yet:

   .. code-block:: python

      # Future validity is NOT checked by is_expired
      tomorrow = timezone.now() + timedelta(days=1)
      coupon = Coupon(valid_at=tomorrow, expired_at=None)

      print(coupon.is_expired)  # False (correct)
      # But it's also not valid yet! Need custom logic:

      def is_currently_valid(obj):
           now = timezone.now()
           if obj.is_expired:
               return False
           if obj.valid_at and obj.valid_at > now:
               return False
           return True

3. **Timezone Awareness**: Always use timezone-aware datetimes:

   .. code-block:: python

      from django.utils import timezone

      # Correct
      coupon.expired_at = timezone.now() + timedelta(days=30)

      # Wrong
      from datetime import datetime
      coupon.expired_at = datetime.now() + timedelta(days=30)  # Avoid!

4. **Combining with Publishable**: When using both Expirable and Publishable, content must be both published AND not expired:

   .. code-block:: python

      class Article(Publishable, Expirable, models.Model):
           title = models.CharField(max_length=200)

           def is_available(self):
               """Check if article is published and not expired."""
               return self.is_published and not self.is_expired

Permalinkable
-------------

**Purpose**: Add URL-friendly slugs with automatic generation.

**Module**: ``apps.common.behaviors.permalinkable``

Fields Added
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field Name
     - Type
     - Description
   * - ``slug``
     - SlugField
     - URL-friendly identifier (unique, auto-generated if blank)

Methods Added
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Method Name
     - Description
   * - ``get_url_kwargs(**kwargs)``
     - Returns URL keyword arguments for use in URL patterns

Source Code
~~~~~~~~~~~

.. code-block:: python

   from typing import Any, Dict
   from django.core.validators import validate_slug
   from django.db import models
   from django.db.models.signals import pre_save
   from django.dispatch import receiver
   from django.utils.text import slugify

   class Permalinkable(models.Model):
       """A behavior mixin that adds permalink/slug functionality."""
       slug = models.SlugField(
           null=True,
           blank=True,
           validators=[validate_slug],
           unique=True,
           help_text="URL-friendly version of the name. Auto-generated if blank.",
       )

       class Meta:
           abstract = True

       def get_url_kwargs(self, **kwargs) -> dict[str, Any]:
           """Get URL keyword arguments for use in URL patterns."""
           kwargs.update(getattr(self, "url_kwargs", {}))
           return kwargs

   @receiver(pre_save)
   def pre_save_slug(sender, instance, *args, **kwargs):
       """Auto-generate slug from slug_source if not set."""
       if hasattr(sender, "mro") and Permalinkable in sender.mro():
           if not instance.slug and hasattr(instance, "slug_source"):
               instance.slug = slugify(instance.slug_source)

Use Cases
~~~~~~~~~

1. **SEO-Friendly URLs**: Use readable URLs like ``/blog/my-first-post/`` instead of ``/blog/123/``
2. **Permanent Links**: Slugs provide stable URLs even if titles change
3. **Readability**: Users can understand URL content before clicking
4. **Social Sharing**: Readable URLs are more shareable on social media
5. **API Endpoints**: Use slugs as resource identifiers

Code Examples
~~~~~~~~~~~~~

**Basic Usage**:

.. code-block:: python

   from django.db import models
   from apps.common.behaviors import Permalinkable

   class Article(Permalinkable, models.Model):
       title = models.CharField(max_length=200)
       content = models.TextField()

       @property
       def slug_source(self):
           """Source field for automatic slug generation."""
           return self.title

       def get_absolute_url(self):
           """Return the URL for this article."""
           return f"/articles/{self.slug}/"

   # Create an article - slug is auto-generated
   article = Article.objects.create(
       title="My First Article"
   )
   print(article.slug)  # "my-first-article"

**Manual Slug**:

.. code-block:: python

   # Manually set a custom slug
   article = Article.objects.create(
       title="My Article",
       slug="custom-slug"
   )
   print(article.slug)  # "custom-slug"

**URL Patterns**:

.. code-block:: python

   # urls.py
   from django.urls import path
   from . import views

   urlpatterns = [
       path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
   ]

   # views.py
   from django.shortcuts import get_object_or_404, render

   def article_detail(request, slug):
       article = get_object_or_404(Article, slug=slug)
       return render(request, 'article_detail.html', {'article': article})

**Using ``get_url_kwargs()``**:

.. code-block:: python

   class Article(Permalinkable, models.Model):
       title = models.CharField(max_length=200)
       category = models.CharField(max_length=50)

       @property
       def slug_source(self):
           return self.title

       @property
       def url_kwargs(self):
           """Additional URL kwargs."""
           return {'category': self.category}

       def get_absolute_url(self):
           from django.urls import reverse
           return reverse('article_detail', kwargs=self.get_url_kwargs(slug=self.slug))

   # urls.py
   path('articles/<str:category>/<slug:slug>/', views.article_detail)

**Handling Duplicates**:

.. code-block:: python

   from django.utils.text import slugify
   from django.db import IntegrityError

   class Article(Permalinkable, models.Model):
       title = models.CharField(max_length=200)

       @property
       def slug_source(self):
           return self.title

       def save(self, *args, **kwargs):
           """Generate unique slug if needed."""
           if not self.slug:
               base_slug = slugify(self.slug_source)
               slug = base_slug
               counter = 1

               # Keep trying until we find a unique slug
               while Article.objects.filter(slug=slug).exists():
                   slug = f"{base_slug}-{counter}"
                   counter += 1

               self.slug = slug

           super().save(*args, **kwargs)

   # Create articles with same title
   article1 = Article.objects.create(title="My Article")
   article2 = Article.objects.create(title="My Article")

   print(article1.slug)  # "my-article"
   print(article2.slug)  # "my-article-1"

Gotchas and Important Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Define ``slug_source``**: The auto-generation requires a ``slug_source`` property:

   .. code-block:: python

      # Wrong: No slug_source defined
      class Article(Permalinkable, models.Model):
           title = models.CharField(max_length=200)

      article = Article.objects.create(title="Test")
      print(article.slug)  # None (not generated!)

      # Right: Define slug_source
      class Article(Permalinkable, models.Model):
           title = models.CharField(max_length=200)

           @property
           def slug_source(self):
               return self.title

2. **Uniqueness Constraint**: Slugs must be unique. Handle duplicates in your save method (see example above).

3. **Slug Characters**: Slugs are lowercase and only contain letters, numbers, hyphens, and underscores:

   .. code-block:: python

      from django.utils.text import slugify

      print(slugify("Hello World!"))  # "hello-world"
      print(slugify("C++ Programming"))  # "c-programming"
      print(slugify("Café"))  # "cafe"

4. **Changing Slugs and SEO**: Once published, changing slugs breaks existing links. Consider:

   .. code-block:: python

      class Article(Permalinkable, models.Model):
           title = models.CharField(max_length=200)
           old_slugs = models.JSONField(default=list, blank=True)

           @property
           def slug_source(self):
               return self.title

           def save(self, *args, **kwargs):
               # Track old slugs for redirects
               if self.pk and self.slug:
                   try:
                       old = Article.objects.get(pk=self.pk)
                       if old.slug != self.slug and old.slug not in self.old_slugs:
                           self.old_slugs.append(old.slug)
                   except Article.DoesNotExist:
                       pass
               super().save(*args, **kwargs)

5. **Signal Pre-save**: The slug generation happens in a ``pre_save`` signal. If you override ``save()``, the signal still runs.

Locatable
---------

**Purpose**: Add geographic location data to models.

**Module**: ``apps.common.behaviors.locatable``

Fields Added
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field Name
     - Type
     - Description
   * - ``address``
     - ForeignKey(Address)
     - Reference to an Address model (nullable)
   * - ``longitude``
     - FloatField
     - Geographic longitude coordinate (nullable)
   * - ``latitude``
     - FloatField
     - Geographic latitude coordinate (nullable)

Properties Added
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Property Name
     - Description
   * - ``has_coordinates``
     - Returns True if both latitude and longitude are set
   * - ``coordinates``
     - Returns (latitude, longitude) tuple or None

Source Code
~~~~~~~~~~~

.. code-block:: python

   from typing import Optional
   from django.db import models

   class Locatable(models.Model):
       """A behavior mixin that adds location-related fields."""
       address = models.ForeignKey(
           "common.Address", null=True, blank=True, on_delete=models.SET_NULL
       )
       longitude = models.FloatField(null=True, blank=True)
       latitude = models.FloatField(null=True, blank=True)

       @property
       def has_coordinates(self) -> bool:
           """Check if the object has valid geographic coordinates."""
           return self.latitude is not None and self.longitude is not None

       @property
       def coordinates(self) -> tuple[float, float] | None:
           """Get the coordinates as a latitude/longitude tuple."""
           if self.has_coordinates:
               return (self.latitude, self.longitude)
           return None

       class Meta:
           abstract = True

Use Cases
~~~~~~~~~

1. **Store Locators**: Find nearby stores or locations
2. **Event Venues**: Track where events take place
3. **User Profiles**: Store user locations
4. **Delivery Tracking**: Track package or vehicle locations
5. **Geographic Analysis**: Analyze data by location

Code Examples
~~~~~~~~~~~~~

**Basic Usage**:

.. code-block:: python

   from django.db import models
   from apps.common.behaviors import Timestampable, Locatable

   class Restaurant(Timestampable, Locatable, models.Model):
       name = models.CharField(max_length=200)
       cuisine = models.CharField(max_length=100)

   # Create a restaurant with coordinates
   restaurant = Restaurant.objects.create(
       name="Joe's Pizza",
       cuisine="Italian",
       latitude=40.7589,  # New York City
       longitude=-73.9851
   )

   print(restaurant.has_coordinates)  # True
   print(restaurant.coordinates)  # (40.7589, -73.9851)

**Using Address Relationship**:

.. code-block:: python

   from apps.common.models import Address

   # Create an address
   address = Address.objects.create(
       street="123 Main St",
       city="New York",
       state="NY",
       postal_code="10001",
       country="US"
   )

   # Associate with restaurant
   restaurant = Restaurant.objects.create(
       name="Joe's Pizza",
       address=address,
       latitude=40.7589,
       longitude=-73.9851
   )

   print(restaurant.address.street)  # "123 Main St"

**Distance Queries (with GeoDjango)**:

.. code-block:: python

   # First, set up GeoDjango in your settings
   # Then use PointField instead of separate lat/lng

   # With standard fields, calculate distance manually:
   from math import radians, sin, cos, sqrt, atan2

   def haversine_distance(lat1, lon1, lat2, lon2):
       """Calculate distance between two points in kilometers."""
       R = 6371  # Earth's radius in kilometers

       lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
       dlat = lat2 - lat1
       dlon = lon2 - lon1

       a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
       c = 2 * atan2(sqrt(a), sqrt(1-a))
       return R * c

   # Find restaurants near a location
   user_lat, user_lng = 40.7580, -73.9855

   nearby_restaurants = []
   for restaurant in Restaurant.objects.all():
       if restaurant.has_coordinates:
           distance = haversine_distance(
               user_lat, user_lng,
               restaurant.latitude, restaurant.longitude
           )
           if distance <= 5:  # Within 5 km
               nearby_restaurants.append((restaurant, distance))

   # Sort by distance
   nearby_restaurants.sort(key=lambda x: x[1])

**Integration with Mapping APIs**:

.. code-block:: python

   class Restaurant(Timestampable, Locatable, models.Model):
       name = models.CharField(max_length=200)

       def get_map_url(self):
           """Generate Google Maps URL."""
           if not self.has_coordinates:
               return None
           return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"

       def get_static_map_url(self, width=400, height=300):
           """Generate static map image URL."""
           if not self.has_coordinates:
               return None
           return (
               f"https://maps.googleapis.com/maps/api/staticmap?"
               f"center={self.latitude},{self.longitude}"
               f"&zoom=15&size={width}x{height}"
               f"&markers=color:red%7C{self.latitude},{self.longitude}"
               f"&key=YOUR_API_KEY"
           )

**Geocoding Addresses**:

.. code-block:: python

   import requests

   class Restaurant(Timestampable, Locatable, models.Model):
       name = models.CharField(max_length=200)

       def geocode_address(self, api_key):
           """Geocode the address to get coordinates."""
           if not self.address:
               return False

           # Using Google Geocoding API
           address_str = f"{self.address.street}, {self.address.city}, {self.address.state}"
           url = "https://maps.googleapis.com/maps/api/geocode/json"
           params = {'address': address_str, 'key': api_key}

           response = requests.get(url, params=params)
           data = response.json()

           if data['status'] == 'OK':
               location = data['results'][0]['geometry']['location']
               self.latitude = location['lat']
               self.longitude = location['lng']
               self.save()
               return True

           return False

Gotchas and Important Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Coordinate Precision**: Float fields have limited precision. For high-precision applications, use DecimalField:

   .. code-block:: python

      # Custom implementation with higher precision
      class PreciseLocatable(models.Model):
           latitude = models.DecimalField(
               max_digits=9, decimal_places=6, null=True, blank=True
           )
           longitude = models.DecimalField(
               max_digits=9, decimal_places=6, null=True, blank=True
           )

2. **Latitude/Longitude Ranges**: Valid ranges are -90 to 90 for latitude, -180 to 180 for longitude:

   .. code-block:: python

      from django.core.validators import MinValueValidator, MaxValueValidator

      class ValidatedLocatable(models.Model):
           latitude = models.FloatField(
               null=True, blank=True,
               validators=[MinValueValidator(-90), MaxValueValidator(90)]
           )
           longitude = models.FloatField(
               null=True, blank=True,
               validators=[MinValueValidator(-180), MaxValueValidator(180)]
           )

3. **Coordinate Order**: The mixin uses (latitude, longitude), but some APIs use (longitude, latitude). Be careful:

   .. code-block:: python

      # Locatable: (lat, lng)
      coords = restaurant.coordinates  # (40.7589, -73.9851)

      # Some APIs expect (lng, lat)
      geojson_coords = coords[::-1]  # Reverse for GeoJSON

4. **GeoDjango vs Simple Coordinates**: For complex spatial queries, consider using GeoDjango's PointField instead:

   .. code-block:: python

      # With GeoDjango (more powerful)
      from django.contrib.gis.db import models as gis_models

      class Restaurant(models.Model):
           location = gis_models.PointField(geography=True, null=True)

           # Enables distance queries:
           # Restaurant.objects.filter(
           #     location__distance_lte=(user_point, D(km=5))
           # )

5. **Address vs Coordinates**: You can have an address without coordinates or coordinates without an address:

   .. code-block:: python

      # Address but no coordinates
      restaurant = Restaurant(address=address, latitude=None, longitude=None)

      # Coordinates but no address
      restaurant = Restaurant(address=None, latitude=40.7589, longitude=-73.9851)

      # Both
      restaurant = Restaurant(address=address, latitude=40.7589, longitude=-73.9851)

Annotatable
-----------

**Purpose**: Allow models to have associated notes or comments.

**Module**: ``apps.common.behaviors.annotatable``

Fields Added
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field Name
     - Type
     - Description
   * - ``notes``
     - ManyToManyField(Note)
     - Many-to-many relationship with the Note model

Properties Added
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Property Name
     - Description
   * - ``has_notes``
     - Returns True if the object has any associated notes

Source Code
~~~~~~~~~~~

.. code-block:: python

   from django.db import models

   class Annotatable(models.Model):
       """A behavior mixin that allows models to have associated notes."""
       notes = models.ManyToManyField("common.Note")

       @property
       def has_notes(self) -> bool:
           """Check if the object has any associated notes."""
           return self.notes.exists()

       class Meta:
           abstract = True

Use Cases
~~~~~~~~~

1. **Internal Comments**: Add admin/staff notes to any object
2. **Audit Trails**: Track why changes were made
3. **Support Tickets**: Attach notes to customer issues
4. **Review Comments**: Store internal review feedback
5. **Collaboration**: Allow team members to leave notes on shared items

Code Examples
~~~~~~~~~~~~~

**Basic Usage**:

.. code-block:: python

   from django.db import models
   from django.contrib.auth import get_user_model
   from apps.common.behaviors import Timestampable, Annotatable
   from apps.common.models import Note

   User = get_user_model()

   class SupportTicket(Timestampable, Annotatable, models.Model):
       title = models.CharField(max_length=200)
       description = models.TextField()
       status = models.CharField(max_length=20)

   # Create a ticket
   ticket = SupportTicket.objects.create(
       title="Login Issue",
       description="User cannot log in",
       status="open"
   )

   # Add a note
   user = User.objects.first()
   note = Note.objects.create(
       text="Checked database, user account is active",
       author=user
   )
   ticket.notes.add(note)

   print(ticket.has_notes)  # True
   print(ticket.notes.count())  # 1

**Helper Method for Adding Notes**:

.. code-block:: python

   class SupportTicket(Timestampable, Annotatable, models.Model):
       title = models.CharField(max_length=200)
       description = models.TextField()
       status = models.CharField(max_length=20)

       def add_note(self, text, author):
           """Add a note to this ticket."""
           note = Note.objects.create(text=text, author=author)
           self.notes.add(note)
           return note

       def get_recent_notes(self, limit=5):
           """Get the most recent notes."""
           return self.notes.order_by('-created_at')[:limit]

   # Usage
   ticket.add_note("Contacted user for more details", staff_user)
   recent = ticket.get_recent_notes()

**Displaying Notes in Templates**:

.. code-block:: django

   {# templates/ticket_detail.html #}
   <div class="ticket">
       <h2>{{ ticket.title }}</h2>
       <p>{{ ticket.description }}</p>

       {% if ticket.has_notes %}
       <div class="notes">
           <h3>Internal Notes</h3>
           {% for note in ticket.notes.all %}
           <div class="note">
               <p>{{ note.text }}</p>
               <small>
                   By {{ note.author_display_name }}
                   on {{ note.created_at|date:"Y-m-d H:i" }}
               </small>
           </div>
           {% endfor %}
       </div>
       {% endif %}
   </div>

**Filtering by Notes**:

.. code-block:: python

   # Get all tickets with notes
   tickets_with_notes = SupportTicket.objects.filter(notes__isnull=False).distinct()

   # Get tickets with notes by a specific user
   tickets_with_user_notes = SupportTicket.objects.filter(
       notes__author=user
   ).distinct()

   # Get tickets with notes containing specific text
   tickets = SupportTicket.objects.filter(
       notes__text__icontains="urgent"
   ).distinct()

**Admin Integration**:

.. code-block:: python

   from django.contrib import admin

   class NoteInline(admin.TabularInline):
       model = SupportTicket.notes.through
       extra = 1
       fields = ['note']

   @admin.register(SupportTicket)
   class SupportTicketAdmin(admin.ModelAdmin):
       list_display = ['title', 'status', 'note_count', 'created_at']
       inlines = [NoteInline]

       def note_count(self, obj):
           """Display number of notes."""
           return obj.notes.count()
       note_count.short_description = 'Notes'

**Anonymous Notes**:

.. code-block:: python

   # Notes support anonymous authorship (from Authorable)
   note = Note.objects.create(
       text="Anonymous feedback",
       author=user,
       is_author_anonymous=True
   )
   ticket.notes.add(note)

   print(note.author_display_name)  # "Anonymous"

Gotchas and Important Notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Many-to-Many Relationship**: Notes can be shared across multiple objects:

   .. code-block:: python

      # One note can be attached to multiple tickets
      shared_note = Note.objects.create(text="Related to incident #123", author=user)
      ticket1.notes.add(shared_note)
      ticket2.notes.add(shared_note)

      # Both tickets now have this note
      print(ticket1.has_notes)  # True
      print(ticket2.has_notes)  # True

2. **Use ``distinct()`` in Queries**: Many-to-many relationships can cause duplicate results:

   .. code-block:: python

      # Wrong: May have duplicates
      tickets = SupportTicket.objects.filter(notes__author=user)

      # Right: Remove duplicates
      tickets = SupportTicket.objects.filter(notes__author=user).distinct()

3. **Note Deletion**: Deleting a note removes it from all associated objects:

   .. code-block:: python

      note.delete()  # Removed from all tickets

      # To remove from just one ticket:
      ticket.notes.remove(note)  # Note still exists, just not linked

4. **Performance with Large Note Sets**: Loading all notes can be expensive. Use pagination or limits:

   .. code-block:: python

      # Wrong: Loads all notes
      all_notes = ticket.notes.all()

      # Better: Limit results
      recent_notes = ticket.notes.order_by('-created_at')[:10]

      # Or use pagination
      from django.core.paginator import Paginator
      paginator = Paginator(ticket.notes.order_by('-created_at'), 10)
      page_notes = paginator.get_page(1)

5. **Permission Control**: Add custom methods to control who can view/add notes:

   .. code-block:: python

      class SupportTicket(Timestampable, Annotatable, models.Model):
           title = models.CharField(max_length=200)

           def can_view_notes(self, user):
               """Check if user can view notes."""
               return user.is_staff or self.created_by == user

           def can_add_notes(self, user):
               """Check if user can add notes."""
               return user.is_staff

Advanced Usage
==============

Combining Multiple Mixins
--------------------------

Method Resolution Order (MRO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python uses the C3 linearization algorithm to determine the Method Resolution Order when multiple classes are inherited. Understanding MRO is crucial when combining mixins:

.. code-block:: python

   # The order matters!
   class BlogPost(Timestampable, Authorable, Publishable, models.Model):
       title = models.CharField(max_length=200)

   # Check the MRO
   print(BlogPost.__mro__)
   # Output: (BlogPost, Timestampable, Authorable, Publishable, models.Model, ...)

**Key Rules**:

1. **Left-to-right**: Classes are searched from left to right
2. **Depth-first**: Parent classes are searched before siblings
3. **Common base last**: Django models.Model should always be last

**Best Practice Order**:

.. code-block:: python

   # Recommended order (general to specific)
   class MyModel(
       Timestampable,      # Most generic - timestamps
       Authorable,         # Content creation tracking
       Publishable,        # Content lifecycle
       Expirable,          # Time constraints
       Locatable,          # Geographic data
       Permalinkable,      # URL structure
       Annotatable,        # Meta information
       models.Model,       # Always last!
   ):
       # Your fields here
       pass

Recommended Combinations
~~~~~~~~~~~~~~~~~~~~~~~~

**Content Management System**:

.. code-block:: python

   class Article(Timestampable, Authorable, Publishable, Permalinkable, models.Model):
       """Blog posts, articles, news items."""
       title = models.CharField(max_length=200)
       content = models.TextField()

       @property
       def slug_source(self):
           return self.title

**E-commerce Products**:

.. code-block:: python

   class Product(Timestampable, Permalinkable, models.Model):
       """Products in an online store."""
       name = models.CharField(max_length=200)
       price = models.DecimalField(max_digits=10, decimal_places=2)

       @property
       def slug_source(self):
           return self.name

**Event Management**:

.. code-block:: python

   class Event(Timestampable, Locatable, Expirable, Permalinkable, models.Model):
       """Events with location and validity period."""
       name = models.CharField(max_length=200)
       start_time = models.DateTimeField()

       @property
       def slug_source(self):
           return self.name

**Support Tickets**:

.. code-block:: python

   class SupportTicket(Timestampable, Authorable, Annotatable, models.Model):
       """Customer support tickets with internal notes."""
       title = models.CharField(max_length=200)
       description = models.TextField()
       status = models.CharField(max_length=20)

**Promotional Campaigns**:

.. code-block:: python

   class Campaign(Timestampable, Publishable, Expirable, models.Model):
       """Marketing campaigns with publish and expiry dates."""
       name = models.CharField(max_length=200)
       description = models.TextField()

Anti-patterns to Avoid
~~~~~~~~~~~~~~~~~~~~~~

**Don't Combine Conflicting Behaviors**:

.. code-block:: python

   # Bad: Combining mixins with similar fields
   class CustomTimestampable(models.Model):
       created = models.DateTimeField(auto_now_add=True)
       class Meta:
           abstract = True

   # This creates conflicts!
   class MyModel(Timestampable, CustomTimestampable, models.Model):
       pass  # Both have creation timestamps but different field names

**Don't Overload with Too Many Mixins**:

.. code-block:: python

   # Bad: Too many mixins makes the model hard to understand
   class OverloadedModel(
       Mixin1, Mixin2, Mixin3, Mixin4, Mixin5,
       Mixin6, Mixin7, Mixin8, models.Model
   ):
       pass  # What does this model even do?

   # Better: Only include what you need
   class FocusedModel(Timestampable, Authorable, models.Model):
       pass

**Don't Forget models.Model**:

.. code-block:: python

   # Bad: Missing models.Model
   class Article(Timestampable, Authorable):
       title = models.CharField(max_length=200)

   # Good: Always include models.Model last
   class Article(Timestampable, Authorable, models.Model):
       title = models.CharField(max_length=200)

Creating Custom Mixins
-----------------------

Step-by-Step Guide
~~~~~~~~~~~~~~~~~~

**Step 1: Define Your Mixin**

.. code-block:: python

   # apps/common/behaviors/prioritizable.py
   from django.db import models

   class Prioritizable(models.Model):
       """A mixin for models that need priority ordering."""

       PRIORITY_LOW = 'low'
       PRIORITY_MEDIUM = 'medium'
       PRIORITY_HIGH = 'high'
       PRIORITY_URGENT = 'urgent'

       PRIORITY_CHOICES = [
           (PRIORITY_LOW, 'Low'),
           (PRIORITY_MEDIUM, 'Medium'),
           (PRIORITY_HIGH, 'High'),
           (PRIORITY_URGENT, 'Urgent'),
       ]

       priority = models.CharField(
           max_length=10,
           choices=PRIORITY_CHOICES,
           default=PRIORITY_MEDIUM
       )
       priority_order = models.IntegerField(default=50)

       class Meta:
           abstract = True
           ordering = ['priority_order', '-created_at']

       @property
       def is_urgent(self) -> bool:
           """Check if item is marked as urgent."""
           return self.priority == self.PRIORITY_URGENT

       def set_priority(self, priority):
           """Set priority and update ordering."""
           self.priority = priority
           priority_map = {
               self.PRIORITY_LOW: 100,
               self.PRIORITY_MEDIUM: 50,
               self.PRIORITY_HIGH: 25,
               self.PRIORITY_URGENT: 1,
           }
           self.priority_order = priority_map.get(priority, 50)

**Step 2: Export Your Mixin**

.. code-block:: python

   # apps/common/behaviors/__init__.py
   from .timestampable import Timestampable
   from .authorable import Authorable
   # ... other imports ...
   from .prioritizable import Prioritizable  # Add your mixin

   __all__ = [
       "Timestampable",
       "Authorable",
       # ... other exports ...
       "Prioritizable",  # Export it
   ]

**Step 3: Use Your Mixin**

.. code-block:: python

   from django.db import models
   from apps.common.behaviors import Timestampable, Prioritizable

   class Task(Timestampable, Prioritizable, models.Model):
       title = models.CharField(max_length=200)
       description = models.TextField()

   # Usage
   task = Task.objects.create(title="Fix bug", description="Critical bug in login")
   task.set_priority(Task.PRIORITY_URGENT)
   task.save()

   print(task.is_urgent)  # True

Testing Strategy
~~~~~~~~~~~~~~~~

**Create Tests for Your Mixin**:

.. code-block:: python

   # apps/common/behaviors/tests/test_prioritizable.py
   import unittest
   from unittest import mock
   from apps.common.behaviors.prioritizable import Prioritizable

   class TestPrioritizableDirect(unittest.TestCase):
       """Direct tests for Prioritizable without database."""

       def test_fields(self):
           """Test the fields are defined correctly."""
           self.assertTrue(hasattr(Prioritizable, "priority"))
           self.assertTrue(hasattr(Prioritizable, "priority_order"))

       def test_is_urgent_property(self):
           """Test is_urgent property."""
           obj = mock.MagicMock(spec=Prioritizable)

           obj.priority = Prioritizable.PRIORITY_URGENT
           self.assertTrue(Prioritizable.is_urgent.fget(obj))

           obj.priority = Prioritizable.PRIORITY_LOW
           self.assertFalse(Prioritizable.is_urgent.fget(obj))

       def test_set_priority(self):
           """Test set_priority method."""
           obj = mock.MagicMock(spec=Prioritizable)

           Prioritizable.set_priority(obj, Prioritizable.PRIORITY_URGENT)
           self.assertEqual(obj.priority, Prioritizable.PRIORITY_URGENT)
           self.assertEqual(obj.priority_order, 1)

           Prioritizable.set_priority(obj, Prioritizable.PRIORITY_LOW)
           self.assertEqual(obj.priority, Prioritizable.PRIORITY_LOW)
           self.assertEqual(obj.priority_order, 100)

**Run Tests**:

.. code-block:: bash

   # Run your mixin tests
   python apps/common/behaviors/tests/test_prioritizable.py

   # Or with pytest
   pytest apps/common/behaviors/tests/test_prioritizable.py

Contribution Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

If adding a mixin to this project template:

1. **Follow Naming Conventions**: Use "-able" suffix (Timestampable, Authorable)
2. **Keep It Generic**: Mixins should be domain-agnostic
3. **Document Thoroughly**: Include docstrings, examples, and gotchas
4. **Write Tests**: Both unit tests and integration tests
5. **Update This Guide**: Add your mixin to the documentation
6. **Consider Backward Compatibility**: Don't break existing models

Migration & Integration Guide
==============================

Adding Mixins to Existing Models
---------------------------------

Step-by-Step Process
~~~~~~~~~~~~~~~~~~~~

**Step 1: Add the Mixin to Your Model**

.. code-block:: python

   # Before
   class Article(models.Model):
       title = models.CharField(max_length=200)
       content = models.TextField()

   # After
   from apps.common.behaviors import Timestampable

   class Article(Timestampable, models.Model):
       title = models.CharField(max_length=200)
       content = models.TextField()

**Step 2: Create and Run Migration**

.. code-block:: bash

   # Generate migration
   python manage.py makemigrations

   # Review the migration file
   # It should add created_at and modified_at fields

   # Apply migration
   python manage.py migrate

**Step 3: Handle Existing Data (if needed)**

If you have existing records, you may need a data migration:

.. code-block:: python

   # migrations/0002_populate_timestamps.py
   from django.db import migrations
   from django.utils import timezone

   def populate_timestamps(apps, schema_editor):
       Article = apps.get_model('app_name', 'Article')
       now = timezone.now()

       # Update all existing records
       Article.objects.filter(created_at__isnull=True).update(
           created_at=now,
           modified_at=now
       )

   class Migration(migrations.Migration):
       dependencies = [
           ('app_name', '0001_add_timestampable'),
       ]

       operations = [
           migrations.RunPython(populate_timestamps),
       ]

Migration Strategies
~~~~~~~~~~~~~~~~~~~~

**Strategy 1: Nullable Fields (Easiest)**

Make mixin fields nullable initially:

.. code-block:: python

   # Custom implementation for gradual rollout
   class Article(models.Model):
       title = models.CharField(max_length=200)
       # Add fields manually as nullable first
       created_at = models.DateTimeField(null=True, blank=True)
       modified_at = models.DateTimeField(null=True, blank=True)

   # Later, add the mixin and make fields required
   class Article(Timestampable, models.Model):
       title = models.CharField(max_length=200)

**Strategy 2: Default Values**

Provide defaults in the migration:

.. code-block:: python

   # In migration file
   migrations.AddField(
       model_name='article',
       name='created_at',
       field=models.DateTimeField(auto_now_add=True, default=timezone.now),
       preserve_default=False,
   )

**Strategy 3: Backfill Data**

Use a data migration to populate fields from existing data:

.. code-block:: python

   def backfill_author_data(apps, schema_editor):
       Article = apps.get_model('app_name', 'Article')

       for article in Article.objects.all():
           # Try to determine author from related data
           if hasattr(article, 'creator'):
               article.author = article.creator
               article.authored_at = article.created_at
               article.save()

Removing Mixins Safely
-----------------------

Process
~~~~~~~

**Step 1: Remove Mixin from Model**

.. code-block:: python

   # Before
   class Article(Timestampable, Authorable, models.Model):
       title = models.CharField(max_length=200)

   # After
   class Article(Timestampable, models.Model):
       title = models.CharField(max_length=200)

**Step 2: Create Migration**

.. code-block:: bash

   python manage.py makemigrations

**Step 3: Review Before Applying**

.. code-block:: python

   # Migration will remove fields!
   # migrations/0003_remove_authorable.py
   operations = [
       migrations.RemoveField(model_name='article', name='author'),
       migrations.RemoveField(model_name='article', name='is_author_anonymous'),
       migrations.RemoveField(model_name='article', name='authored_at'),
   ]

**Step 4: Backup Data (if needed)**

.. code-block:: bash

   # Export data before removing fields
   python manage.py dumpdata app_name.Article > article_backup.json

**Step 5: Apply Migration**

.. code-block:: bash

   python manage.py migrate

Data Migration Examples
-----------------------

Example 1: Populate Slug from Title
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # migrations/0004_populate_slugs.py
   from django.db import migrations
   from django.utils.text import slugify

   def populate_slugs(apps, schema_editor):
       Article = apps.get_model('app_name', 'Article')

       for article in Article.objects.filter(slug__isnull=True):
           base_slug = slugify(article.title)
           slug = base_slug
           counter = 1

           # Ensure uniqueness
           while Article.objects.filter(slug=slug).exists():
               slug = f"{base_slug}-{counter}"
               counter += 1

           article.slug = slug
           article.save()

   class Migration(migrations.Migration):
       dependencies = [
           ('app_name', '0003_add_permalinkable'),
       ]

       operations = [
           migrations.RunPython(populate_slugs),
       ]

Example 2: Convert Published Boolean to Publishable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # migrations/0005_convert_to_publishable.py
   from django.db import migrations
   from django.utils import timezone

   def convert_published_to_publishable(apps, schema_editor):
       Article = apps.get_model('app_name', 'Article')

       for article in Article.objects.all():
           # If old is_published was True, set published_at
           if article.is_published:
               article.published_at = article.created_at
           article.save()

   def reverse_conversion(apps, schema_editor):
       Article = apps.get_model('app_name', 'Article')

       for article in Article.objects.all():
           article.is_published = bool(article.published_at)
           article.save()

   class Migration(migrations.Migration):
       dependencies = [
           ('app_name', '0004_add_publishable'),
       ]

       operations = [
           migrations.RunPython(
               convert_published_to_publishable,
               reverse_conversion
           ),
       ]

Testing Behaviors
=================

Testing Strategy Overview
-------------------------

The behavior mixins in this project are tested at two levels:

1. **Unit Tests**: Test mixin functionality in isolation without database
2. **Integration Tests**: Test mixins with real Django models and database

Both test approaches are included in the codebase.

Unit Testing Mixins
-------------------

Unit tests use mocks to test mixin properties and methods without database overhead:

.. code-block:: python

   # apps/common/behaviors/tests/test_behaviors.py
   import unittest
   from unittest import mock
   from apps.common.behaviors.timestampable import Timestampable

   class TestTimestampableDirect(unittest.TestCase):
       """Direct tests for Timestampable without database."""

       def test_fields(self):
           """Test the fields are defined correctly."""
           self.assertTrue(hasattr(Timestampable, "created_at"))
           self.assertTrue(hasattr(Timestampable, "modified_at"))

           # Get field instances
           created_at_field = Timestampable._meta.get_field("created_at")
           modified_at_field = Timestampable._meta.get_field("modified_at")

           self.assertEqual(created_at_field.auto_now_add, True)
           self.assertEqual(modified_at_field.auto_now, True)

Run unit tests:

.. code-block:: bash

   python apps/common/behaviors/tests/test_behaviors.py

Integration Testing with Models
--------------------------------

Create test models that use mixins:

.. code-block:: python

   # apps/myapp/tests.py
   from django.test import TestCase
   from django.contrib.auth import get_user_model
   from apps.common.behaviors import Timestampable, Authorable

   User = get_user_model()

   class TestArticleModel(TestCase):
       """Integration tests for Article model with behaviors."""

       def setUp(self):
           self.user = User.objects.create_user(
               username='testuser',
               email='test@example.com',
               password='password123'
           )

       def test_timestamps_auto_set(self):
           """Test that timestamps are automatically set."""
           from myapp.models import Article

           article = Article.objects.create(
               title="Test Article",
               content="Test content",
               author=self.user
           )

           self.assertIsNotNone(article.created_at)
           self.assertIsNotNone(article.modified_at)

       def test_author_display_name(self):
           """Test author display name property."""
           from myapp.models import Article

           article = Article.objects.create(
               title="Test Article",
               content="Test content",
               author=self.user
           )

           self.assertEqual(article.author_display_name, str(self.user))

           # Test anonymous
           article.is_author_anonymous = True
           self.assertEqual(article.author_display_name, "Anonymous")

Run integration tests:

.. code-block:: bash

   python manage.py test myapp.tests.TestArticleModel

Writing Tests for Custom Mixins
--------------------------------

When creating custom mixins, follow this testing template:

.. code-block:: python

   # apps/common/behaviors/tests/test_custom_mixin.py
   import unittest
   from unittest import mock
   from django.test import TestCase
   from apps.common.behaviors.custom_mixin import CustomMixin

   # Unit tests
   class TestCustomMixinDirect(unittest.TestCase):
       """Direct tests without database."""

       def test_fields_exist(self):
           """Test that expected fields are defined."""
           self.assertTrue(hasattr(CustomMixin, "field_name"))

       def test_property(self):
           """Test properties with mocks."""
           obj = mock.MagicMock(spec=CustomMixin)
           obj.field_name = "value"
           result = CustomMixin.property_name.fget(obj)
           self.assertEqual(result, "expected")

       def test_method(self):
           """Test methods with mocks."""
           obj = mock.MagicMock(spec=CustomMixin)
           CustomMixin.method_name(obj, "arg")
           # Assert expected behavior

   # Integration tests (if needed)
   class TestCustomMixinIntegration(TestCase):
       """Integration tests with database."""

       def test_with_real_model(self):
           """Test mixin with a real Django model."""
           # Create test model instance
           # Test behavior with database
           pass

Factory Patterns with Mixins
-----------------------------

Use factory_boy for creating test fixtures with mixins:

.. code-block:: python

   # apps/myapp/factories.py
   import factory
   from factory.django import DjangoModelFactory
   from django.contrib.auth import get_user_model
   from myapp.models import Article

   User = get_user_model()

   class UserFactory(DjangoModelFactory):
       class Meta:
           model = User

       username = factory.Sequence(lambda n: f"user{n}")
       email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")

   class ArticleFactory(DjangoModelFactory):
       class Meta:
           model = Article

       title = factory.Sequence(lambda n: f"Article {n}")
       content = factory.Faker('paragraph')
       author = factory.SubFactory(UserFactory)

       # Timestampable fields are auto-set
       # Publishable fields can be customized
       @factory.post_generation
       def published(obj, create, extracted, **kwargs):
           if extracted:
               obj.publish()
               obj.save()

**Usage in Tests**:

.. code-block:: python

   from myapp.factories import ArticleFactory

   class TestArticle(TestCase):
       def test_published_article(self):
           """Test a published article."""
           article = ArticleFactory(published=True)

           self.assertTrue(article.is_published)
           self.assertIsNotNone(article.published_at)

       def test_multiple_articles(self):
           """Test creating multiple articles."""
           articles = ArticleFactory.create_batch(5)

           self.assertEqual(len(articles), 5)
           for article in articles:
               self.assertIsNotNone(article.created_at)
               self.assertIsNotNone(article.author)

Conclusion
==========

Behavior mixins provide a powerful, flexible way to add reusable functionality to Django models. By following the patterns and practices outlined in this guide, you can:

- Reduce code duplication across your models
- Maintain consistency in field names and behavior
- Easily add new functionality to multiple models at once
- Test behaviors independently from business logic
- Create more maintainable and scalable Django applications

**Key Takeaways**:

1. Use mixins for generic, reusable model functionality
2. Order matters when combining multiple mixins
3. Always include ``models.Model`` as the last base class
4. Test mixins both in isolation and with real models
5. Document custom mixins thoroughly for your team

For more information about Django models and best practices, see:

- `Django Model Documentation <https://docs.djangoproject.com/en/stable/topics/db/models/>`_
- `Python MRO <https://www.python.org/download/releases/2.3/mro/>`_
- `Django Migrations <https://docs.djangoproject.com/en/stable/topics/migrations/>`_
