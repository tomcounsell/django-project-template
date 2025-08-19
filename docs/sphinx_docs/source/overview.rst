Overview
========

The Django Project Template provides a solid foundation for building Django applications with best practices in:

* Clean architecture with reusable components
* Model behaviors for common patterns
* API design and implementation
* Frontend integration with HTMX and Tailwind
* Testing strategies and conventions
* Documentation and development workflows

Project Structure
----------------

The project follows a modular approach with these key components:

* **apps/common**: Core models, behaviors, and utilities
* **apps/api**: REST API endpoints and serializers
* **apps/public**: Web interface and HTMX components
* **apps/ai**: AI integration features
* **apps/integration**: Third-party service integrations

Key Features
-----------

* **Behavior Mixins**: Reusable model components for common patterns (timestampable, authorable, etc.)
* **HTMX Integration**: Simplified interactive interfaces with minimal JavaScript
* **Django Rest Framework API**: Well-structured API endpoints with proper authentication
* **Team-based Permissions**: Multi-tenant capabilities with team membership
* **Comprehensive Test Suite**: High test coverage with pytest
* **Modern Admin Interface**: Enhanced admin experience with Django Unfold
