Team Model
==========

The Team model enables multi-tenant functionality with team-based permissions.

.. automodule:: apps.common.models.team
   :members:
   :undoc-members:
   :show-inheritance:

Fields
------

.. autoclass:: apps.common.models.team.Team
   :members:
   :undoc-members:
   :exclude-members: DoesNotExist, MultipleObjectsReturned

Team Membership
--------------

Team membership is handled through a many-to-many relationship with the User model.