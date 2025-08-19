Development Patterns
==================

Key patterns and architectural approaches used in the Django Project Template.

Behavior Mixins
--------------

Behavior mixins provide reusable functionality through composition rather than inheritance.

Example usage:

.. code-block:: python

    from django.db import models
    from apps.common.behaviors.timestampable import Timestampable
    from apps.common.behaviors.authorable import Authorable
    
    class BlogPost(Timestampable, Authorable, models.Model):
        title = models.CharField(max_length=100)
        content = models.TextField()

This approach ensures:

- Clear separation of concerns
- Reusable behaviors across models
- Easy composition of functionality
- Testable behaviors in isolation

HTMX Integration
--------------

The project uses HTMX for interactive UI without heavy JavaScript.

Key HTMX patterns:

1. **HTMXView Class**: Base class for HTMX-specific views
2. **Partial Templates**: Templates designed for HTMX updates
3. **hx-* Attributes**: Used directly in templates for HTMX functionality
4. **Targeted Updates**: Using hx-target for specific DOM updates

Example HTMX view:

.. code-block:: python

    from apps.public.helpers.htmx_view import HTMXView
    
    class TodoListView(HTMXView):
        template_name = "todos/todo_list.html"
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["todos"] = Todo.objects.filter(user=self.request.user)
            return context

Team-Based Multi-Tenancy
----------------------

The project implements team-based multi-tenancy for collaborative features.

Implementation includes:

1. **Team Model**: Central model for team management
2. **Team Membership**: Many-to-many relationship with User model
3. **Team Context**: Views maintain team context through request session
4. **Team Permissions**: Authorization based on team membership

API Design
---------

The API follows RESTful principles with DRF:

1. **Serializer Hierarchy**: Base serializers extended for specific needs
2. **Multiple Authentication**: Session and API key authentication
3. **Permissions System**: Both object and action-level permissions
4. **Versioning**: API versioning through URL or header
