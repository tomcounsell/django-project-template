# apps/insights/models/summary.py
from django.db import models
from apps.common.behaviors.timestampable import Timestampable


class Summary(Timestampable):
    """
    Model to store the dataset summary and key metrics for a specific time period.
    """

    start_date = models.DateField(help_text="Start date of the data period.")
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
        ordering = ["-start_date"]
        unique_together = ("start_date",)  # Adjusted to remove end_date
        verbose_name_plural = "Summaries"


class KeyMetric(Timestampable):
    """
    Model to store individual key metrics related to a Summary.
    """

    summary = models.ForeignKey(
        Summary,
        related_name="key_metrics",
        on_delete=models.CASCADE,
        help_text="The summary this key metric belongs to.",
    )
    name = models.CharField(max_length=100, help_text="Name of the metric.")
    value = models.FloatField(help_text="Numeric value of the metric.")

    def __str__(self):
        return f"{self.name}: {self.value} (Summary ID: {self.summary.id})"

    class Meta:
        unique_together = ("summary", "name")
        ordering = ["name"]
