# apps/insights/models.py

from django.db import models


class Summary(models.Model):
    """
    Model to store the dataset summary and key metrics for a specific time period.
    """

    # Choices for summary type, in case we have summaries for different periods in the future
    SUMMARY_TYPE_CHOICES = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    summary_type = models.CharField(
        max_length=20,
        choices=SUMMARY_TYPE_CHOICES,
        default="weekly",
        help_text="Type of the summary (e.g., weekly, monthly).",
    )
    start_date = models.DateField(help_text="Start date of the data period.")
    end_date = models.DateField(help_text="End date of the data period.")
    dataset_summary = models.TextField(
        help_text="A concise English summary of the dataset."
    )
    # Optionally, store the data source file path or identifier
    data_source = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="File path or identifier of the data source.",
    )
    date_created = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the summary was created."
    )
    date_updated = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the summary was last updated."
    )

    def __str__(self):
        return f"Summary ({self.summary_type.capitalize()}) from {self.start_date} to {self.end_date}"

    class Meta:
        ordering = ["-start_date"]
        unique_together = ("summary_type", "start_date", "end_date")
        verbose_name_plural = "Summaries"


class KeyMetric(models.Model):
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
