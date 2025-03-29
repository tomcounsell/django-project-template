from rest_framework import serializers
from apps.common.models import TodoItem, User


class UserReferenceSerializer(serializers.ModelSerializer):
    """Simple serializer for user reference in TodoItem."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "full_name")

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class TodoItemSerializer(serializers.ModelSerializer):
    """Serializer for the TodoItem model."""

    assignee = UserReferenceSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True,
    )
    is_completed = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    time_remaining_display = serializers.CharField(read_only=True)

    class Meta:
        model = TodoItem
        fields = (
            "id",
            "title",
            "description",
            "priority",
            "category",
            "status",
            "assignee",
            "assignee_id",
            "due_at",
            "completed_at",
            "created_at",
            "modified_at",
            "is_completed",
            "is_overdue",
            "days_until_due",
            "time_remaining_display",
        )
        read_only_fields = ("id", "created_at", "modified_at", "completed_at")

    def validate_status(self, value):
        """Update completed_at when status is changed to DONE."""
        if (
            value == TodoItem.STATUS_DONE
            and self.instance
            and self.instance.status != TodoItem.STATUS_DONE
        ):
            self.context["set_completed_at"] = True
        elif (
            value != TodoItem.STATUS_DONE
            and self.instance
            and self.instance.status == TodoItem.STATUS_DONE
        ):
            self.context["clear_completed_at"] = True
        return value

    def update(self, instance, validated_data):
        """Handle status changes that affect completed_at."""
        if self.context.get("set_completed_at"):
            instance.complete()
            # Remove status from validated_data since complete() already sets it
            validated_data.pop("status", None)
        elif self.context.get("clear_completed_at"):
            instance.reopen()
            # Remove status from validated_data since reopen() already sets it
            validated_data.pop("status", None)

        return super().update(instance, validated_data)


class TodoItemListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing TodoItems."""

    assignee_name = serializers.SerializerMethodField()

    class Meta:
        model = TodoItem
        fields = (
            "id",
            "title",
            "priority",
            "category",
            "status",
            "assignee_name",
            "due_at",
            "is_overdue",
        )

    def get_assignee_name(self, obj):
        if not obj.assignee:
            return None
        name = f"{obj.assignee.first_name} {obj.assignee.last_name}".strip()
        return name or obj.assignee.username
