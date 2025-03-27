from django.urls import path
from rest_framework import routers
from apps.api.views import user, twilio, todo, api_key

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
    
    # Twilio webhook endpoint
    path("webhooks/twilio/", twilio.twilio_webhook, name="twilio-webhook"),
]

# # JWT AUTH
# from rest_framework_simplejwt import views as jwt_views
# urlpatterns += [
#     path('auth/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('auth/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
#     path('auth/token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
# ]
