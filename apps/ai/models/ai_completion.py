from django.db import models
from django.contrib.postgres.fields import JSONField

from apps.common.behaviors import timestampable
from apps.ai.models.prompt_template import PromptTemplate


class AICompletion(timestampable.Timestampable, models.Model):
    """
    Stores AI completions from various providers.
    Records both the input prompt and the generated completion, as well as metadata.
    """

    # Relationships
    prompt_template = models.ForeignKey(
        PromptTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completions",
    )

    # Input details
    prompt_input = models.TextField()
    prompt_variables = JSONField(default=dict, blank=True)
    context_text = models.TextField(blank=True)

    # Output details
    completion_text = models.TextField()

    # Provider details
    provider = models.CharField(max_length=100)  # e.g. "openai", "anthropic"
    model = models.CharField(max_length=100)  # e.g. "gpt-4", "claude-3", etc.
    temperature = models.FloatField(null=True, blank=True)

    # Usage metrics
    usage_tokens = models.IntegerField(default=0)
    usage_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    # Flags
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "AI Completion"
        verbose_name_plural = "AI Completions"
        ordering = ["-created_at"]

    def __str__(self):
        completion_date = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"{self.provider}/{self.model} completion from {completion_date}"
