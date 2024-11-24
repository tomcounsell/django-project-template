# apps/insights/models/task_record.py
from django.db import models
from django_q.models import Task
from apps.insights.models.summary import Summary
from apps.insights.models.comparison import Comparison


class TaskRecord(models.Model):
    """
    Model to record additional information about tasks executed via Django-Q2.
    """

    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        help_text="The Django-Q task associated with this record.",
    )
    task_name = models.CharField(
        max_length=255, help_text="Name of the task function being executed."
    )
    status = models.CharField(
        max_length=50, help_text="Status of the task (e.g., Pending, Success, Failed)."
    )
    started_at = models.DateTimeField(help_text="Timestamp when the task started.")
    completed_at = models.DateTimeField(
        null=True, blank=True, help_text="Timestamp when the task completed."
    )
    result = models.TextField(
        null=True, blank=True, help_text="Result of the task, if applicable."
    )
    error = models.TextField(
        null=True, blank=True, help_text="Error message if the task failed."
    )
    summary = models.ForeignKey(
        Summary,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Associated summary, if applicable.",
    )
    comparison = models.ForeignKey(
        Comparison,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Associated comparison, if applicable.",
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Start date of the data period the task is processing.",
    )

    def __str__(self):
        return f"Task Record for Task ID: {self.task.id}"

    class Meta:
        verbose_name = "Task Record"
        verbose_name_plural = "Task Records"
        ordering = ["-started_at"]
