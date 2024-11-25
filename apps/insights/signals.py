# apps/insights/signals.py
from django.dispatch import receiver
from django_q.signals import post_execute
from django_q.models import Task
from apps.insights.models.task_record import TaskRecord
from apps.insights.models.summary import Summary  # Import as needed
from apps.insights.models.comparison import Comparison  # Import as needed
import logging

# Set up the logger for this module
logger = logging.getLogger(__name__)


@receiver(post_execute)
def handle_post_execute(sender, task, **kwargs):
    """
    Handles the post-execute signal to create or update a TaskRecord.
    Triggered after each Django-Q task execution.
    """
    logger.info(f"Post-execute signal received for task ID: {task.get('id')}")

    try:
        # Fetch the Task object using the task ID
        task_obj = Task.objects.get(id=task["id"])
        status = "Success" if task.get("success") else "Failed"
        error_message = task.get("result") if not task.get("success") else None

        # Create or update the TaskRecord
        task_record, created = TaskRecord.objects.update_or_create(
            task=task_obj,
            defaults={
                "task_name": task.get("name"),
                "status": status,
                "started_at": task_obj.started,
                "completed_at": task_obj.stopped,
                "result": task.get("result") if task.get("success") else None,
                "error": error_message,
            },
        )

        # Log whether a new TaskRecord was created or updated
        if created:
            logger.info(f"Created TaskRecord for Task ID {task_obj.id}")
        else:
            logger.info(f"Updated TaskRecord for Task ID {task_obj.id}")

    except Task.DoesNotExist:
        logger.error(f"Task with ID {task.get('id')} does not exist.")
    except Exception as e:
        logger.exception(
            f"Error handling post_execute signal for Task ID {task.get('id')}: {e}"
        )
