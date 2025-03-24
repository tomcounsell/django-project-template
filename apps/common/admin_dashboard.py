"""
Custom admin dashboard for the Django project template.
"""
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from apps.common.models import Team

User = get_user_model()


def get_admin_dashboard(request, context=None):
    """
    Generate dashboard widgets and stats for the admin index page.
    
    This function is called by Django Unfold to customize the admin dashboard.
    
    Args:
        request: The current request object
        context: The current context dictionary
        
    Returns:
        Modified context with dashboard widgets
    """
    # Initialize context if not provided
    if context is None:
        context = {}
    
    # Only show dashboard for staff users
    if not request.user.is_staff:
        return context
    
    # Get model counts
    user_count = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    team_count = Team.objects.count()
    active_teams = Team.objects.filter(is_active=True).count()
    
    # Define dashboard widgets
    widgets = [
        {
            "title": _("Dashboard"),
            "widgets": [
                {
                    "title": _("Users Summary"),
                    "template": "admin/dashboard/users_summary.html",
                    "context": {
                        "total_users": user_count,
                        "active_users": active_users,
                        "staff_users": staff_users,
                    },
                    "column": 1,
                    "order": 0,
                },
                {
                    "title": _("Teams Summary"),
                    "template": "admin/dashboard/teams_summary.html",
                    "context": {
                        "total_teams": team_count,
                        "active_teams": active_teams,
                    },
                    "column": 1,
                    "order": 1,
                },
                {
                    "title": _("Recent Activity"),
                    "template": "admin/dashboard/recent_activity.html",
                    "column": 2,
                    "order": 0,
                },
            ],
        }
    ]
    
    # Add widgets to context
    context["widgets"] = widgets
    
    return context