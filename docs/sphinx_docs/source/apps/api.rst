API App
=======

The `api` app provides REST API endpoints for the Django Project Template.

Overview
--------

The API app uses Django REST Framework to expose core functionality through RESTful endpoints. It includes:

- User management endpoints
- Todo item management
- API key generation and management
- Webhook handlers for third-party services

Serializers
----------

.. automodule:: apps.api.serializers
   :members:

User Serializers
~~~~~~~~~~~~~~

.. automodule:: apps.api.serializers.user
   :members:
   :undoc-members:
   :show-inheritance:

Todo Serializers
~~~~~~~~~~~~~~

.. automodule:: apps.api.serializers.todo
   :members:
   :undoc-members:
   :show-inheritance:

Views
-----

API Views for different resources.

User API
~~~~~~~

.. automodule:: apps.api.views.user
   :members:
   :undoc-members:
   :show-inheritance:

Todo API
~~~~~~~

.. automodule:: apps.api.views.todo
   :members:
   :undoc-members:
   :show-inheritance:

API Key Management
~~~~~~~~~~~~~~~~

.. automodule:: apps.api.views.api_key
   :members:
   :undoc-members:
   :show-inheritance:

Webhooks
~~~~~~~

.. automodule:: apps.api.views.stripe
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: apps.api.views.twilio
   :members:
   :undoc-members:
   :show-inheritance:
