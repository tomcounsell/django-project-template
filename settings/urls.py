from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from settings import DEBUG, LOCAL

# Create OpenAPI schema for documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Django Project API",
        default_version='v1',
        description="RESTful API for the Django Project Template",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("", include("apps.public.urls", namespace="public")),
    
    # API URLs
    path('api/', include('apps.api.urls')),
    
    # API Documentation with Swagger/ReDoc
    re_path(r'^api/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Built-In AUTH and ADMIN
admin.autodiscover()
admin.site.site_header = "ProjectName Content Database"
admin.site.site_title = "ProjectName"
admin.site.site_url = None
admin.site.index_title = "Content Database"
urlpatterns += [
    path("admin/", admin.site.urls),
]

# DEBUG MODE
if DEBUG:
    import debug_toolbar

    dev_url_patterns = []
    dev_url_patterns.append(
        path("__debug__/", include(debug_toolbar.urls)),
    )
    if LOCAL:
        dev_url_patterns.append(
            path("__reload__/", include("django_browser_reload.urls")),
        )
    urlpatterns = dev_url_patterns + urlpatterns