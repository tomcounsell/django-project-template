Behavior Mixins
===============

Django behavior mixins are abstract model classes that encapsulate common functionalities that can be reused across different models. They follow the DRY (Don't Repeat Yourself) principle by providing reusable behaviors.

Available Mixins
----------------

The project includes the following behavior mixins:

Timestampable
~~~~~~~~~~~~~

**Location**: ``apps/common/behaviors/timestampable.py``

Tracks creation and modification timestamps for an object.

**Fields**:
- ``created_at``: When the object was created
- ``modified_at``: When the object was last modified

**Example Usage**:

.. code-block:: python

   from django.db import models
   from apps.common.behaviors import Timestampable

   class Product(Timestampable, models.Model):
       name = models.CharField(max_length=100)
       price = models.DecimalField(max_digits=10, decimal_places=2)

Authorable
~~~~~~~~~~

**Location**: ``apps/common/behaviors/authorable.py``

Associates content with an author and tracks authorship information.

**Fields**:
- ``author``: Foreign key to the User model
- ``is_author_anonymous``: Boolean flag for anonymous content
- ``authored_at``: When the content was authored

**Properties**:
- ``author_display_name``: Returns "Anonymous" or the author's name

Describable
~~~~~~~~~~~

**Location**: ``apps/common/behaviors/describable.py``

Adds SEO and description capabilities to models.

**Fields**:
- ``name``: Primary name/title
- ``description``: Detailed description
- ``short_description``: Brief summary

Permalinkable
~~~~~~~~~~~~~

**Location**: ``apps/common/behaviors/permalinkable.py``

Provides URL slug functionality for SEO-friendly URLs.

**Fields**:
- ``slug``: URL-safe identifier

Publishable
~~~~~~~~~~~

**Location**: ``apps/common/behaviors/publishable.py``

Controls content visibility and publication status.

**Fields**:
- ``is_public``: Whether content is publicly visible
- ``published_at``: When content was published

Archivable
~~~~~~~~~~

**Location**: ``apps/common/behaviors/archivable.py``

Enables soft deletion and archival of content.

**Fields**:
- ``is_archived``: Whether content is archived
- ``archived_at``: When content was archived

For more detailed information, see the :doc:`../../../BEHAVIOR_MIXINS` guide.