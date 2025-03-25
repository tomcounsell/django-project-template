from django.urls import path
from rest_framework import routers
from apps.api.views import user

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

# Auth endpoints will be added later
urlpatterns = [
    # Example auth endpoints (currently commented out)
    # path("auth/csrf/", csrf_view, name="csrf"),
    # path("auth/login/", login_view, name="login"),
    # path("auth/logout/", logout_view, name="logout"),
    # path("auth/password/change/", password_change_view, name="password_change"),
    # path("auth/me/", me_view, name="me"),
]

# # JWT AUTH
# from rest_framework_simplejwt import views as jwt_views
# urlpatterns += [
#     path('auth/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('auth/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
#     path('auth/token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
# ]
