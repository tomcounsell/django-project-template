"""
DEPRECATED: This module is kept for backward compatibility only.

Please use the updated version in apps.public.helpers.main_content_view instead.
The new implementation offers improved functionality and better documentation.

To migrate:
1. Import MainContentView from apps.public.helpers instead:
   from apps.public.helpers import MainContentView

2. If you need HTMX-specific functionality, use HTMXView:
   from apps.public.helpers import HTMXView

3. For session management, use the TeamSessionMixin:
   from apps.public.helpers import TeamSessionMixin
"""

# For backward compatibility, import and re-export the new implementation
from apps.public.helpers.main_content_view import MainContentView
