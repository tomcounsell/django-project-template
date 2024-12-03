from django.db import models


class StatisticalOverview(models.Model):
    dataset_name = models.CharField(max_length=255)
    column_name = models.CharField(max_length=255)
    count = models.IntegerField()
    mean = models.FloatField(null=True, blank=True)
    std = models.FloatField(null=True, blank=True)
    min = models.FloatField(null=True, blank=True)
    percentile_25 = models.FloatField(null=True, blank=True)
    median = models.FloatField(null=True, blank=True)
    percentile_75 = models.FloatField(null=True, blank=True)
    max = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dataset_name} - {self.column_name} Stats"


# KeyMetric New Field Example
class KeyMetric(models.Model):
    statistical_overview = models.OneToOneField(
        StatisticalOverview, on_delete=models.CASCADE, related_name="key_metric"
    )

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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Key Metric for {self.statistical_overview.column_name}"
