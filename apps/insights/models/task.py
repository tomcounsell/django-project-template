# apps/common/models/scheduled_task.py
from django.db import models
from common.behaviors.timestampable import Timestampable
from common.behaviors.uuidable import UUIDable


class ScheduledTask(UUIDable, Timestampable):
    # Represents a scheduled task with execution details.

    name = models.CharField(
        max_length=100, help_text="A descriptive name for the scheduled task."
    )
    task = models.CharField(
        max_length=200, help_text="The Python path of the task function."
    )
    schedule_type = models.CharField(
        max_length=50,
        choices=[
            ("cron", "Cron"),
            ("interval", "Interval"),
            ("once", "One-time"),
        ],
        help_text="The type of scheduling (cron, interval, one-time).",
    )
    schedule = models.JSONField(
        help_text="The schedule details in JSON format (e.g., cron params)."
    )
    args = models.JSONField(
        null=True, blank=True, help_text="Arguments to pass to the task."
    )
    kwargs = models.JSONField(
        null=True, blank=True, help_text="Keyword arguments to pass to the task."
    )
    last_run_at = models.DateTimeField(
        null=True, blank=True, help_text="The last time the task was run."
    )
    next_run_at = models.DateTimeField(
        null=True, blank=True, help_text="The next scheduled run time."
    )
    enabled = models.BooleanField(
        default=True, help_text="Indicates whether the task is active."
    )

    def __str__(self):
        return self.name
