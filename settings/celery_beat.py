# settings/celery_beat.py
import os
import logging
from django.db import transaction
from celery import Celery

from django_celery_beat.models import PeriodicTask
from django_celery_beat.models import PeriodicTasks
from django_celery_beat.schedulers import DatabaseScheduler

app = Celery("scheduled_tasks_ai")
app.conf.update(
    broker_url=os.environ.get("REDIS_STREAMS_URL"),
    result_backend=os.environ.get("REDIS_STREAMS_URL"),
    beat_schedule={
        # Example task
        "sample_task": {
            "task": "your_project_name.tasks.sample_task",
            "schedule": 3600.0,  # Run every hour
        },
    },
)


class DatabaseSchedulerWithCleanup(DatabaseScheduler):
    def setup_schedule(self):
        schedule = self.app.conf.beat_schedule
        with transaction.atomic():
            num, info = (
                PeriodicTask.objects.exclude(task__startswith="celery.")
                .exclude(name__in=schedule.keys())
                .delete()
            )
            logging.info("Removed %d obsolete periodic tasks.", num)
            if num > 0:
                PeriodicTasks.update_changed()
        super(DatabaseSchedulerWithCleanup, self).setup_schedule()
