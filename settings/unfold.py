"""
Django Unfold admin configuration settings
"""
from django.utils.translation import gettext_lazy as _

# Admin site configuration - used in urls.py
ADMIN_SITE_HEADER = "ProjectName Content Database"
ADMIN_SITE_TITLE = "ProjectName"
ADMIN_SITE_URL = None
ADMIN_INDEX_TITLE = "Content Database"

# Django Unfold settings - minimal version to get it working
UNFOLD = {
    "SITE_TITLE": "ProjectName Admin",
    "SITE_HEADER": "ProjectName Content Database",
    "SITE_URL": "/",
    "SITE_ICON": None,
    "DASHBOARD_CALLBACK": "apps.common.admin_dashboard.get_admin_dashboard",
    "STYLES": [
        "css/output.css",
    ],
    "COLORS": {
        "primary": {
            "50": "239, 246, 255",
            "100": "219, 234, 254",
            "200": "191, 219, 254",
            "300": "147, 197, 253",
            "400": "96, 165, 250",
            "500": "59, 130, 246",
            "600": "37, 99, 235",
            "700": "29, 78, 216",
            "800": "30, 64, 175",
            "900": "30, 58, 138",
        },
    },
}