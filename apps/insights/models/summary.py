# apps/insights/models/summary.py
from Typing import Type
from django.core.exceptions import ValidationError
from django.db import models
from apps.common.behaviors.timestampable import Timestampable
from apps.common.behaviors.uuidable import UUIDable


class Summary(Timestampable, UUIDable):
    """
    Model to store the dataset summary and key metrics for a specific time period.
    """

    objects: Type[models.Manager] = (
        models.Manager()
    )  # Explicitly add the objects manager for MyPy

    start_date: models.DateField = models.DateField(
        help_text=(
            "The starting date of the dataset's time period. This is used for identifying "
            "and organizing summaries. It should correspond to the first day of the data coverage."
        ),
        db_index=True,  # Index added for faster filtering and ordering by start_date
    )
    dataset_summary: models.TextField = models.TextField(
        help_text=(
            "A concise English summary of the dataset, highlighting key patterns, trends, "
            "or anomalies for the specified time period."
        )
    )
    data_source: models.CharField = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=(
            "Optional. A file path, URL, or identifier for the source of the dataset. "
            "Useful for traceability or referencing the original data."
        ),
    )

    def clean(self):
        """
        Validates that the dataset_summary is not empty and does not exceed a reasonable length.
        """
        if not self.dataset_summary:
            raise ValidationError("The dataset summary cannot be empty.")
        if len(self.dataset_summary) > 2000:  # Example max length
            raise ValidationError("The dataset summary cannot exceed 2000 characters.")

    def __str__(self):
        """
        Returns a string representation of the Summary, including the start date and data source if available.
        """
        if self.data_source:
            return f"Summary from {self.start_date} (Source: {self.data_source})"
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

    summary: models.ForeignKey = models.ForeignKey(
        Summary,
        related_name="key_metrics",
        on_delete=models.CASCADE,
        help_text="The summary this key metric belongs to.",
    )
    name: models.CharField = models.CharField(
        max_length=100,
        help_text="Name of the metric.",
        db_index=True,  # Index for filtering by name
    )
    value: models.FloatField = models.FloatField(
        help_text="Numeric value of the metric."
    )

    def clean(self):
        """
        Validates that the value is non-negative if negative values are not expected.
        """
        if self.value < 0:
            raise ValidationError(
                f"The value for metric '{self.name}' cannot be negative."
            )

    def __str__(self):
        """
        Returns a descriptive string including the metric's name, value, and associated summary's date.
        """
        # Use .start_date from the related Summary object
        return f"Metric: {self.name}, Value: {self.value} ({self.summary.start_date if self.summary else 'No Summary exists'})"

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
