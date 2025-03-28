from django.urls import path, re_path
from rest_framework import routers, permissions
from apps.api.views import user, twilio, todo, api_key, stripe
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

# These auth endpoints are commented out since they don't exist yet
# Will be implemented in future
"""
from apps.common.views.auth import (
    csrf_view,
    login_view,
    logout_view,
    me_view,
    password_change_view,
)
"""

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

# API V1

app_name = "api"
api_router = routers.DefaultRouter()

api_router.register(
    r"users",
    user.UserViewSet,
)

api_router.register(
    r"todos",
    todo.TodoItemViewSet,
)

api_router.register(
    r"user-api-keys",
    api_key.UserAPIKeyViewSet,
    basename="user-api-key"
)

api_router.register(
    r"team-api-keys",
    api_key.TeamAPIKeyViewSet,
    basename="team-api-key"
)

# Auth endpoints will be added later
urlpatterns = api_router.urls + [
    # Example auth endpoints (currently commented out)
    # path("auth/csrf/", csrf_view, name="csrf"),
    # path("auth/login/", login_view, name="login"),
    # path("auth/logout/", logout_view, name="logout"),
    # path("auth/password/change/", password_change_view, name="password_change"),
    # path("auth/me/", me_view, name="me"),
    
    # Webhook endpoints
    path("webhooks/twilio/", twilio.twilio_webhook, name="twilio-webhook"),
    path("webhooks/stripe/", stripe.stripe_webhook_view, name="stripe-webhook"),
    
    # API Documentation with Swagger/ReDoc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# # JWT AUTH
# from rest_framework_simplejwt import views as jwt_views
# urlpatterns += [
#     path('auth/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('auth/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
#     path('auth/token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
# ]
