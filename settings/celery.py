# settings/celery.py
import os
from celery import Celery
from settings.base import TIME_ZONE

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Celery Configuration Options
CELERY_BROKER_URL = os.environ.get("REDIS_STREAMS_URL")  # Use Redis Streams
CELERY_RESULT_BACKEND = os.environ.get("DB_URL")  # Use PostgreSQL
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = int(
    os.environ.get("CELERY_TASK_TIME_LIMIT", 14400)
)  # Default: 4 hours
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True


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
