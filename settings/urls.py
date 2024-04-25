from settings import DEBUG
from django.urls import include, path
from django.contrib import admin
from django.views.generic import TemplateView
from rest_framework.documentation import include_docs_urls
from django.urls import include


urlpatterns = [
    path('', TemplateView.as_view(template_name='pages/home.html'), name="home"),
]

# Django Rest Framework API Docs
API_TITLE, API_DESCRIPTION = "django-project-template API", ""
urlpatterns += [
    path('docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION))
]

# Built-In AUTH and ADMIN
admin.autodiscover()
admin.site.site_header = "django-project-template Content Database"
admin.site.site_title = "django-project-template"
admin.site.site_url = None
admin.site.index_title = "Content Database"
urlpatterns += [
    path('admin/', admin.site.urls),
]

# DEBUG MODE
if DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
