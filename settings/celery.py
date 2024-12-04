# settings/celery.py
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Celery Configuration Options
CELERY_BROKER_URL = os.getenv("REDIS_URL")
CELERY_RESULT_BACKEND = os.getenv("POSTGRES_URL")
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = int(
    os.environ.get("CELERY_TASK_TIME_LIMIT", 14400)
)  # default 4 hours


class MyCelery(Celery):
    def gen_task_name(self, name, module):
        module = ".".join(
            [dir for dir in module.split(".") if dir not in ("apps", "tasks")]
        )
        return super().gen_task_name(name, module)


app = MyCelery("scheduled_tasks_ai")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
