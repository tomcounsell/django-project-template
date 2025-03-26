from rest_framework import serializers
from apps.common.utilities.processing.serializers import WritableSerializerMethodField
from apps.common.models import User
from typing import Optional


class UserSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(
        required=False,
        allow_null=False,
        allow_blank=False,
        min_length=3,
        max_length=150,
    )
    is_agreed_to_terms = WritableSerializerMethodField(
        deserializer_field=serializers.BooleanField(), required=False
    )
    leap_api_key = WritableSerializerMethodField(
        deserializer_field=serializers.CharField(), required=False
    )
    openai_api_key = WritableSerializerMethodField(
        deserializer_field=serializers.CharField(), required=False
    )
    openai_api_org = WritableSerializerMethodField(
        deserializer_field=serializers.CharField(), required=False
    )
    tnl_auth_token = WritableSerializerMethodField(
        deserializer_field=serializers.CharField(), required=False
    )

    class Meta:
        model = User

        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "organization_name",
            "is_staff",
            "is_premium_member",
            "is_beta_tester",
            "is_agreed_to_terms",
            "created_at",
            "modified_at",
            "leap_api_key",
            "openai_api_key",
            "openai_api_org",
            "tnl_auth_token",
        )

        read_only_fields = ("id", "token", "created_at", "modified_at")

    def get_api_key(
        self, obj, key, masking_start_stop: Optional[tuple[int, int]] = (3, -3)
    ):
        value = obj.api_keys.get(key, "")
        if (
            value
            and masking_start_stop
            and len(value) > max(abs(masking_start_stop[0]), abs(masking_start_stop[1]))
        ):
            return f"{value[:masking_start_stop[0]]}***{value[masking_start_stop[1]:]}"
        elif value:
            return value
        return ""

    def set_api_key(self, key, value):
        self.instance.api_keys[key] = value

    def get_is_agreed_to_terms(self, obj):
        return obj.is_agreed_to_terms

    def set_is_agreed_to_terms(self, value):
        if self.instance:
            self.instance.is_agreed_to_terms = value

    def get_leap_api_key(self, obj):
        return self.get_api_key(obj, "leap_api_key") or obj.api_keys.get(
            "leap", {}
        ).get("api_key", "")

    def set_leap_api_key(self, value):
        self.set_api_key("leap_api_key", value)

    def get_openai_api_key(self, obj):
        return self.get_api_key(obj, "openai_api_key") or obj.api_keys.get(
            "openai", {}
        ).get("api_key", "")

    def set_openai_api_key(self, value):
        self.set_api_key("openai_api_key", value)

    def get_openai_api_org(self, obj):
        return self.get_api_key(obj, "openai_api_org", masking_start_stop=(6, -3))

    def set_openai_api_org(self, value):
        self.set_api_key("openai_api_org", value)

    def get_tnl_auth_token(self, obj):
        return self.get_api_key(obj, "thenextleg_auth_token")

    def set_tnl_auth_token(self, value):
        self.set_api_key("thenextleg_auth_token", value)
