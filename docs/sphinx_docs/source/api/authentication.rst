API Authentication
================

The Django Project Template supports multiple authentication methods for API access.

Session Authentication
--------------------

For browser-based applications, session authentication is available by default.

API Key Authentication
-------------------

For server-to-server communication, API key authentication is provided.

.. automodule:: apps.common.utilities.drf_permissions.api_key
   :members:
   :undoc-members:
   :show-inheritance:

API Key Model
-----------

.. automodule:: apps.common.models.api_key
   :members:
   :undoc-members:
   :show-inheritance:

API Key Generation
----------------

API keys can be generated through the admin interface or via the API key management endpoints.