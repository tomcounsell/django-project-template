"""Django models for chat functionality."""

import uuid
from typing import Optional

from django.db import models

from apps.common.behaviors import Timestampable
from apps.common.models import User


class ChatSession(Timestampable, models.Model):
    """A chat session between a user and the AI assistant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
        null=True,
        blank=True,
        help_text="User associated with this chat session",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Optional title for the chat session",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this session is currently active"
    )
    metadata = models.JSONField(
        default=dict, blank=True, help_text="Additional metadata for the session"
    )

    class Meta:
        ordering = ["-modified_at"]
        indexes = [
            models.Index(fields=["-modified_at"]),
            models.Index(fields=["user", "-modified_at"]),
        ]

    def __str__(self):
        if self.title:
            return f"Chat Session: {self.title}"
        return f"Chat Session {self.id}"

    @property
    def message_count(self) -> int:
        """Get the number of messages in this session."""
        return self.messages.count()

    @property
    def last_message(self) -> Optional["ChatMessage"]:
        """Get the last message in this session."""
        return self.messages.order_by("-created_at").first()

    def generate_title(self) -> str:
        """Generate a title based on the first user message."""
        first_user_message = (
            self.messages.filter(role="user").order_by("created_at").first()
        )
        if first_user_message:
            # Take first 50 characters of the message
            title = first_user_message.content[:50]
            if len(first_user_message.content) > 50:
                title += "..."
            return title
        return "New Chat"


class ChatMessage(Timestampable, models.Model):
    """A single message in a chat session."""

    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
        ("system", "System"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="The chat session this message belongs to",
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, help_text="The role of the message sender"
    )
    content = models.TextField(help_text="The message content")
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for the message (e.g., model used, tokens, etc.)",
    )
    is_processed = models.BooleanField(
        default=True,
        help_text="Whether this message has been processed (useful for async processing)",
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["session", "created_at"]),
            models.Index(fields=["session", "-created_at"]),
        ]

    def __str__(self):
        truncated_content = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"{self.get_role_display()}: {truncated_content}"
