# apps/insights/models.py
from django.db import models
from common.behaviors.timestampable import Timestampable
from common.behaviors.uuidable import UUIDable
from common.behaviors.annotatable import Annotatable
from common.behaviors.authorable import Authorable


class DataSummary(UUIDable, Timestampable, Annotatable, Authorable):
    # Represents a summary of a dataset with key metrics and a description.

    label = models.CharField(
        max_length=50,
        help_text="A label identifying the dataset (e.g., 'Week 1').",
    )
    plain_summary = models.TextField(help_text="An English summary of the dataset.")
    key_metrics = models.JSONField(help_text="Structured key metrics from the dataset.")
    metadata = models.JSONField(
        help_text="Additional metadata about the summary (e.g., filters applied).",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"DataSummary: {self.label}"


class SummaryComparison(UUIDable, Timestampable, Annotatable):
    # Represents a comparison between two week-over-weekDataSummary records.

    summary_1 = models.ForeignKey(
        DataSummary,
        on_delete=models.CASCADE,
        related_name="compared_as_summary_1",
        help_text="The first summary to be compared.",
    )
    summary_2 = models.ForeignKey(
        DataSummary,
        on_delete=models.CASCADE,
        related_name="compared_as_summary_2",
        help_text="The second summary to be compared.",
    )
    comparison_result = models.JSONField(
        help_text="The results of the comparison in JSON format."
    )
    comparison_type = models.CharField(
        max_length=50,
        help_text="The type of comparison (e.g., 'week-over-week').",
        default="week-over-week",
    )

    def __str__(self):
        return f"Comparison: {self.summary_1.label} vs {self.summary_2.label}"
