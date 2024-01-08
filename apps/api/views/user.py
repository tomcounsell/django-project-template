from django.contrib.auth import authenticate
from django.utils import timezone
from django_filters import DateTimeFilter
from django_filters.rest_framework import FilterSet
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.api.serializers.user import UserSerializer
from apps.common.models import User
from apps.common.utilities.drf_permissions import IsCreateAction


class UserFilter(FilterSet):
    last_login = DateTimeFilter(field_name="last_login", lookup_expr="gte")

    class Meta:
        model = User
        fields = (
            "is_active",
            "is_staff",
            "is_beta_tester",
            "is_premium_member",
            "last_login",
            # "api_calls_count",
        )


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    # mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    LIST endpoints:

    - `/users/` ONLY superusers accounts can GET list of all users

    GET endpoint:

    - `/users/123/` returns user object where user_id=123

    POST endpoint:

    - `/users/` with JSON `{"username": char_string}`

        - limit 150 characters or fewer. Letters, digits and @.+-_ only.
        - can use email address as username
        - if username already exists, API returns `400` error with JSON `{"username": ["A user with that username already exists."]}`

    """

    permission_classes = [IsAuthenticated | IsAdminUser]  # IsCreateAction
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter

    def partial_update(self, request, pk=None, *args, **kwargs):
        user = self.get_object()  # Get the user instance

        # Check if email is already in use by another user
        user_account_with_same_email = (
            User.objects.filter(email=request.data.get("email"), is_email_verified=True)
            .exclude(id=user.id)
            .first()
        )
        if user_account_with_same_email:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"status": "user already registered, please login"},
            )

        # Update API keys in user_api_keys JSONField
        api_keys = request.data.get("user_api_keys", {})
        user.user_api_keys.update(api_keys)

        # If user agreed to terms, update agreed_to_terms_at datetime
        if request.data.get("is_agreed_to_terms"):
            user.agreed_to_terms_at = timezone.now()

        # Update other fields
        for attr, value in request.data.items():
            if hasattr(user, attr):
                setattr(user, attr, value)

        user.save()
        return Response(self.get_serializer(user).data)

    def get_queryset(self):
        if self.request.user.is_superuser:
            # if self.lookup_url_kwarg or self.lookup_field:
            #     user = self.get_object()  # Get the user instance
            return User.objects.all()
        else:
            return User.objects.filter(id=self.request.user.id)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def authenticate_with_password_or_code(self, request, pk=None, *args, **kwargs):
        """
        expecting 'four_digit_code' as a string and optionally username, email, or id in endpoint
        use this endpoint to login with a password or a code that was emailed to the user
        correct code passes and validates email, incorrect code fails
        correct password passes, unless email is not verified
        will also fail if not user.is_active (eg. blocked or banned)
        """

        user_accounts = [
            User.objects.filter(id=pk).first(),
            User.objects.filter(
                email=request.data.get("email", "not@email"), is_email_verified=True
            ).first(),
            User.objects.filter(
                email=request.data.get("email", "not@email"), is_email_verified=False
            ).first(),
            User.objects.filter(
                username=request.data.get("username", ""),
                email__isnull=False,
                is_email_verified=True,
            ).first(),
        ]
        success, auth_user = False, None

        if not any([user.is_active for user in user_accounts if user]):
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"status": "active account not found"},
            )

        for user in user_accounts:
            if user and user.is_active:
                # validate four_digit_code and mark email address as verified
                if str(request.data.get("four_digit_code", "VOID")).strip() == str(
                    user.four_digit_login_code
                ):
                    success = True
                    auth_user = user

                elif request.data.get("password") and user.is_email_verified:
                    auth_user = authenticate(
                        request,
                        username=user.username,
                        password=request.data.get("password"),
                    )
                    if auth_user:
                        success = True

                if success:
                    auth_user.is_email_verified = True
                    auth_user.last_login = (
                        timezone.now()
                    )  # note this will cause the four_digit_code to change 👍
                    auth_user.save()
                    serializer = self.get_serializer(auth_user, many=False)
                    return Response(serializer.data)

        if (
            not success
            and not request.data.get("four_digit_code", None)
            and not user.is_email_verified
        ):
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"status": "email not verified, verify email and try again"},
            )

        elif not success:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"status": "password or code incorrect"},
            )

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={"status": "unknown authentication error"},
        )
