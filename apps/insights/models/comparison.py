# apps/insights/models/comparison.py
from django.db import models
from apps.common.behaviors.timestampable import Timestampable  # Importing Timestampable
from apps.insights.models.summary import (
    Summary,
)  # Ensure this import aligns with project structure


class Comparison(Timestampable):
    """
    Model to store the comparison between two summaries.
    """

    summary1 = models.ForeignKey(  # Current Week
        Summary,
        related_name="comparisons_as_summary1",
        on_delete=models.CASCADE,
        help_text="The current week summary being compared.",
    )
    summary2 = models.ForeignKey(  # Past Week
        Summary,
        related_name="comparisons_as_summary2",
        on_delete=models.CASCADE,
        help_text="The past week summary being compared.",
    )
    comparison_summary = models.TextField(
        help_text="A concise summary of differences and similarities between the two summaries."
    )
    start_date = models.DateField(
        help_text="Start date of the current week in the comparison, derived from summary1.",
        editable=False,
    )

    def save(self, *args, **kwargs):
        self.start_date = self.summary1.start_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comparison from {self.start_date}"

    class Meta:
        unique_together = ("summary1", "summary2")
        ordering = ["-created_at"]


class KeyMetricComparison(Timestampable):
    """
    Model to store individual key metric comparisons related to a Comparison.
    """

    comparison = models.ForeignKey(
        Comparison,
        related_name="key_metrics_comparison",
        on_delete=models.CASCADE,
        help_text="The comparison this key metric comparison belongs to.",
    )
    name = models.CharField(
        max_length=100, help_text="Name of the metric being compared."
    )
    value1 = models.FloatField(help_text="Value from the current week.")
    value2 = models.FloatField(help_text="Value from the past week.")
    description = models.TextField(
        help_text="Description of the observed difference or trend.",
        null=True,
        blank=True,
    )
    percentage_difference = models.FloatField(
        help_text="Percentage difference between the two values.", null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if self.value1 and self.value2:
            self.percentage_difference = (
                ((self.value1 - self.value2) / self.value2) * 100
                if self.value2 != 0
                else None
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} Comparison (Comparison ID: {self.comparison.id})"

    class Meta:
        unique_together = ("comparison", "name")
        ordering = ["name"]
