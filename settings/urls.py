from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from settings.env import DEBUG, LOCAL

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("", include("apps.public.urls", namespace="public")),
    
    # API URLs
    path('api/', include('apps.api.urls')),
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