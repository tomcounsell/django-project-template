"""
Django Rest Framework permissions.
"""

from rest_framework import permissions
from apps.common.utilities.drf_permissions.api_key import (
    HasUserAPIKey,
    HasTeamAPIKey,
    HasAnyAPIKey,
)


class IsCreateAction(permissions.BasePermission):
    """
    Allow only create actions for unauthenticated users.
    """

    def has_permission(self, request, view):
        return view.action == "create"
