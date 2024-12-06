from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from settings import DEBUG, LOCAL

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path("", include("apps.public.urls", namespace="public")),
]


# # Django Rest Framework API Docs
# API_TITLE, API_DESCRIPTION = "PhotOps API", ""
# urlpatterns += [
#     path('docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION))
# ]

# Built-In AUTH and ADMIN
admin.autodiscover()
admin.site.site_header = "PhotOps Content Database"
admin.site.site_title = "PhotOps"
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
