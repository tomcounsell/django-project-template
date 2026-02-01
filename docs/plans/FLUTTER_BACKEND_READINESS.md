# Flutter Mobile Backend Readiness Plan

This document outlines the implementation plan for making this Django backend ready to serve a Flutter mobile application.

## Current State

The project has solid infrastructure but is missing critical components:
- REST Framework installed but endpoints removed
- CORS configured but middleware disabled
- No JWT authentication
- API routes commented out

## Implementation Plan

### Phase 1: Enable Core Infrastructure

#### 1.1 Enable CORS Middleware

**File:** `settings/base.py`

Uncomment the CORS middleware in the MIDDLEWARE list:
```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Enable this
    # ... rest of middleware
]
```

**File:** `settings/env.py`

Update CORS configuration for mobile apps:
```python
if LOCAL:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_WHITELIST = [
        "https://localhost",
        "https://127.0.0.1",
        # Add production mobile app domains
    ]

# Allow credentials for authenticated requests
CORS_ALLOW_CREDENTIALS = True

# Allow common headers from mobile clients
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-requested-with",
]
```

#### 1.2 Enable API URL Routes

**File:** `settings/urls.py`

Uncomment API-related URL patterns:
```python
path('api/', include('apps.api.urls')),
path('api/schema/', get_schema_view(...), name='openapi-schema'),
path('api/docs/', TemplateView.as_view(...), name='swagger-ui'),
```

---

### Phase 2: Implement JWT Authentication

#### 2.1 Install Package

```bash
uv add djangorestframework-simplejwt
```

#### 2.2 Configure Settings

**File:** `settings/base.py` or `settings/third_party.py`

```python
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # ... existing settings
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}
```

#### 2.3 Add Token URLs

**File:** `apps/api/urls.py`

```python
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # ... other API routes
]
```

---

### Phase 3: Build Core API Endpoints

#### 3.1 User Serializers

**File:** `apps/api/serializers/user.py`

```python
from rest_framework import serializers
from apps.common.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_email_verified']
        read_only_fields = ['id', 'email', 'is_email_verified']
```

#### 3.2 User Views

**File:** `apps/api/views/user.py`

```python
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.common.models import User
from apps.api.serializers.user import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    """Register a new user account."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update current user's profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDeleteView(APIView):
    """Delete current user's account."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

#### 3.3 Wire Up URLs

**File:** `apps/api/urls.py`

```python
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.api.views.user import (
    UserRegistrationView,
    UserProfileView,
    UserDeleteView,
)

app_name = 'api'

urlpatterns = [
    # Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Management
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/delete/', UserDeleteView.as_view(), name='profile_delete'),
]
```

---

### Phase 4: Re-enable API Documentation

#### 4.1 Configure Swagger/OpenAPI

**File:** `settings/urls.py`

```python
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="Mobile API Documentation",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # ... existing patterns
    path('api/', include('apps.api.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
```

---

### Phase 5: Additional Mobile Endpoints (Optional)

Based on app requirements, consider adding:

#### 5.1 Password Reset Flow
- `POST /api/password/reset/` - Request password reset email
- `POST /api/password/reset/confirm/` - Confirm reset with token

#### 5.2 Email Verification
- `POST /api/verify-email/` - Verify email with code
- `POST /api/verify-email/resend/` - Resend verification email

#### 5.3 Social Authentication
- `POST /api/auth/google/` - Google OAuth login
- `POST /api/auth/apple/` - Apple Sign-in

#### 5.4 Device Management
- `POST /api/devices/` - Register push notification token
- `DELETE /api/devices/{token}/` - Remove device token

---

## Testing Checklist

After implementation, verify:

- [ ] CORS allows requests from Flutter app
- [ ] JWT token obtain works with email/password
- [ ] JWT token refresh extends session
- [ ] Protected endpoints reject unauthenticated requests
- [ ] Protected endpoints accept valid JWT
- [ ] User registration creates account
- [ ] User profile retrieval works
- [ ] API docs accessible at `/api/docs/`

## Flutter Integration Notes

### HTTP Client Setup

```dart
// Example Dio configuration for Flutter
final dio = Dio(BaseOptions(
  baseUrl: 'https://your-api.com/api/',
  headers: {
    'Content-Type': 'application/json',
  },
));

// Add JWT interceptor
dio.interceptors.add(InterceptorsWrapper(
  onRequest: (options, handler) {
    final token = getStoredAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  },
));
```

### Token Storage

Store tokens securely using `flutter_secure_storage` package, not SharedPreferences.

### Token Refresh

Implement automatic token refresh when receiving 401 responses.
