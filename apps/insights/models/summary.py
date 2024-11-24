# apps/insights/models.py

from django.db import models


class Summary(models.Model):
    """
    Model to store the dataset summary and key metrics for a specific week.
    """

    WEEK_CHOICES = [
        (1, "Week 1"),
        (2, "Week 2"),
    ]

    week_number = models.PositiveSmallIntegerField(choices=WEEK_CHOICES)
    dataset_summary = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary for Week {self.week_number}"


class KeyMetric(models.Model):
    """
    Model to store individual key metrics related to a Summary.
    """

    summary = models.ForeignKey(
        Summary, related_name="key_metrics", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    value = models.FloatField()

    def __str__(self):
        return f"{self.name}: {self.value} (Summary ID: {self.summary.id})"

    class Meta:
        unique_together = ("summary", "name")
