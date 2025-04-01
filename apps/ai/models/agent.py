from django.contrib.postgres.fields import JSONField
from django.db import models

from apps.common.behaviors import timestampable


class Agent(timestampable.Timestampable, models.Model):
    """
    Represents an AI agent with configuration for a specific task or purpose.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Default configuration
    default_provider = models.CharField(max_length=100)  # e.g. "openai", "anthropic"
    default_model = models.CharField(max_length=100)  # e.g. "gpt-4", "claude-3"
    default_temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=4000)

    # Agent configuration
    system_prompt = models.TextField()
    context_instructions = models.TextField(blank=True)
    additional_context = JSONField(default=dict, blank=True)

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "AI Agent"
        verbose_name_plural = "AI Agents"
        ordering = ["name"]

    def __str__(self):
        return self.name
