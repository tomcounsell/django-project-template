from datetime import datetime

from django.db import models


class BackgroundJob(models.Model):
    name = models.CharField(max_length=64, null=True)
    description = models.CharField(max_length=1000, null=True, blank=True)

    start_run_at = models.DateTimeField(auto_now_add=True)
    end_run_at = models.DateTimeField(null=True)

    has_errors = models.BooleanField(null=False, default=False)
    is_failed = models.BooleanField(null=False, default=True)
    logs = models.JSONField(default=list, blank=True)

    class Meta:
        abstract = True

    @property
    def execution_time_humanized(self) -> str:
        if not self.start_run_at:
            return ""
        seconds = ((self.end_run_at or datetime.today()) - self.start_run_at).seconds
        hours = seconds // 3600
        seconds -= hours * 3600
        minutes = seconds // 60
        seconds -= minutes * 60
        return (
            (f"{hours} hr, " if hours else "")
            + (f"{minutes} min, " if minutes or hours else "")
            + f"{seconds} s"
        )
