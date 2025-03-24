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
        
        from django.utils import timezone
        # Use timezone.now() which returns an aware datetime
        end_time = self.end_run_at or timezone.now()
        
        # Calculate the time difference in seconds
        delta = end_time - self.start_run_at
        total_seconds = delta.total_seconds()
        
        # Calculate hours, minutes, and seconds
        hours, remainder = divmod(int(total_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Format the string
        return (
            (f"{hours} hr, " if hours else "")
            + (f"{minutes} min, " if minutes or hours else "")
            + f"{seconds} s"
        )
