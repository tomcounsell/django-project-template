# apps/insights/models/summary.py
from django.db import models
from apps.common.behaviors.timestampable import Timestampable
from apps.common.behaviors.uuidable import UUIDable


class Summary(Timestampable, UUIDable):
    """
    Model to store the dataset summary and key metrics for a specific time period.
    """

    start_date = models.DateField(
        help_text="Start date of the data period.",
        db_index=True,  # Index added for faster filtering and ordering by start_date
    )
    dataset_summary = models.TextField(
        help_text="A concise English summary of the dataset."
    )
    data_source = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="File path or identifier of the data source.",
    )

    def __str__(self):
        return f"Summary from {self.start_date}"

    class Meta:
        ordering = [
            "-start_date",
            "-created_at",
        ]  # Added secondary ordering for predictability
        constraints = [
            models.UniqueConstraint(fields=["start_date"], name="unique_start_date"),
        ]
        verbose_name_plural = "Summaries"


class KeyMetric(Timestampable, UUIDable):
    """
    Model to store individual key metrics related to a Summary.
    """

    summary = models.ForeignKey(
        Summary,
        related_name="key_metrics",
        on_delete=models.CASCADE,
        help_text="The summary this key metric belongs to.",
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the metric.",
        db_index=True,  # Index for filtering by name
    )
    value = models.FloatField(help_text="Numeric value of the metric.")

    def __str__(self):
        return f"{self.name}: {self.value} (Summary ID: {self.summary.id})"

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["summary", "name"], name="unique_summary_name"
            ),
        ]
        indexes = [
            models.Index(fields=["summary", "name"]),  # Combined index for performance
        ]
