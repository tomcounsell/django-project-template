# apps/insights/tasks.py
"""
Task definitions for the Insights app.
These tasks integrate with Django-Q to run asynchronously.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django_q.models import Schedule
from django_q.tasks import async_task
from apps.insights.data_pipeline import run_pipeline

logger = logging.getLogger(__name__)


def run_pipeline_task(file_path: str, start_date: str):
    """
    Async task wrapper for running the data pipeline.
    Args:
        file_path (str): Path to the CSV file.
        start_date (str): Starting date for data filtering (YYYY-MM-DD).
    """
    try:
        logger.info(
            f"Task triggered: Running pipeline for {file_path} starting {start_date}"
        )
        run_pipeline(file_path, start_date)
        logger.info("Task completed successfully.")
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise


def schedule_initial_task(file_path: str, start_date: str):
    """
    Schedules the initial task to run 1 minute after creation.
    """
    try:
        logger.info("Scheduling initial task to run 1 minute later...")
        Schedule.objects.create(
            func="apps.insights.tasks.chained_tasks",  # Chain starts here
            args=f"'{file_path}', '{start_date}'",
            schedule_type=Schedule.ONCE,
            next_run=timezone.now() + timedelta(minutes=1),
        )
        logger.info("Initial task scheduled successfully.")
    except Exception as e:
        logger.error(f"Failed to schedule the initial task: {e}")
        raise


# Example trigger for manual testing:
# schedule_initial_task("/path/to/ga4_data.csv", "2024-01-01")
