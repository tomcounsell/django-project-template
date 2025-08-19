Architecture
============

The Django Project Template follows a clean architecture with clear separation of concerns and modular design.

Application Structure
--------------------

.. code-block:: none

    django-project-template/
    ├── apps/                  # All application modules
    │   ├── common/            # Core models and utilities
    │   ├── api/               # REST API endpoints
    │   ├── public/            # Web interface components
    │   ├── ai/                # AI integration features
    │   └── integration/       # Third-party integrations
    ├── settings/              # Project configuration
    ├── templates/             # All HTML templates (centralized)
    ├── static/                # Static assets (centralized)
    └── docs/                  # Project documentation

Key Design Principles
--------------------

1. **Centralized Templates and Static Files**

   Templates and static files are stored in root-level directories rather than within apps, 
   promoting consistency and reducing duplication.

2. **Behavior Mixins**

   Models use behavior mixins (e.g., Timestampable, Authorable) to share common functionality
   without complex inheritance hierarchies.

3. **HTMX-Centric Frontend**

   Frontend interactions are implemented primarily using HTMX, reducing the need for 
   custom JavaScript while maintaining modern UX capabilities.

4. **Comprehensive Testing**

   Every component has extensive test coverage using pytest, with specific patterns
   for testing models, views, and behaviors.

5. **Clean API Design**

   APIs follow a consistent RESTful design using Django Rest Framework, with 
   standardized serializers and authentication mechanisms.

6. **Modular Integrations**

   Third-party integrations are encapsulated in dedicated modules with clear interfaces,
   making them easy to replace or update.

App Responsibilities
-------------------

**common**
   Core data models, behaviors, and utilities used throughout the application.

**api**
   REST API endpoints, serializers, and authentication.

**public**
   Web interface components, including HTMX views and templates.

**ai**
   Artificial intelligence integrations and models.

**integration**
   Third-party service connections (AWS, Stripe, Twilio, etc.).
