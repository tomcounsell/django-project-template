from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from settings.env import DEBUG, LOCAL
from settings.unfold import ADMIN_SITE_HEADER, ADMIN_SITE_TITLE, ADMIN_SITE_URL, ADMIN_INDEX_TITLE

# Configure Django's built-in admin
admin.autodiscover()
admin.site.site_header = ADMIN_SITE_HEADER
admin.site.site_title = ADMIN_SITE_TITLE
admin.site.site_url = ADMIN_SITE_URL
admin.site.index_title = ADMIN_INDEX_TITLE

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("", include("apps.public.urls", namespace="public")),
    
    # API URLs
    path('api/', include('apps.api.urls')),
    
    # API Schema and Documentation
    path('api/schema/', get_schema_view(
        title="Django Project Template API",
        description="API for Django Project Template",
        version="1.0.0",
    ), name='openapi-schema'),
    
    path('api/docs/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
]

# Admin URL
# Admin configuration is in settings/unfold.py
urlpatterns += [
    path("admin/", admin.site.urls),
]

# DEBUG MODE
if DEBUG:
    import debug_toolbar
    from django.conf import settings
    from django.conf.urls.static import static

    dev_url_patterns = []
    dev_url_patterns.append(
        path("__debug__/", include(debug_toolbar.urls)),
    )
    if LOCAL:
        dev_url_patterns.append(
            path("__reload__/", include("django_browser_reload.urls")),
        )
    urlpatterns = dev_url_patterns + urlpatterns
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)