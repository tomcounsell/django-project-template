"""
Django Rest Framework permissions.
"""

from rest_framework import permissions


class IsCreateAction(permissions.BasePermission):
    """
    Allow only create actions for unauthenticated users.
    """

    def has_permission(self, request, view):
        return view.action == 'create'