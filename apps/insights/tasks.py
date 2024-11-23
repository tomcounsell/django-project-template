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
from apps.insights.services.summary_service import process_week

logger = logging.getLogger(__name__)


def process_week_task(file_path: str, start_date: str, week: int):
    """
    Processes a single week's data and generates an LLM summary.

    Args:
        file_path (str): Path to the CSV file.
        start_date (str): Start date for the week (YYYY-MM-DD).
        week (int): Week number (1 or 2).
    """
    try:
        logger.info(f"Processing Week {week} starting from {start_date}...")
        result = process_week(file_path, start_date, week)
        logger.info(f"Week {week} summary generated successfully.")
        return {
            "dataset_summary": result.dataset_summary,
            "key_metrics": result.key_metrics,
        }
    except Exception as e:
        logger.error(f"Failed to process Week {week}: {e}")
        raise


def schedule_two_summaries(file_path: str, start_date: str):
    """
    Schedules tasks to process Week 1 after a 1-minute delay,
    followed by processing Week 2.
    """
    try:
        logger.info("Scheduling Week 1 task to run in 1 minute...")

        # Schedule Week 1
        Schedule.objects.create(
            func="apps.insights.tasks.process_week_task",
            args=f"'{file_path}', '{start_date}', 1",
            schedule_type=Schedule.ONCE,
            next_run=timezone.now() + timedelta(minutes=1),
        )
        logger.info("Week 1 task scheduled successfully.")

        # Calculate Week 2 start date
        week2_start_date = pd.to_datetime(start_date) + pd.Timedelta(days=7)

        # Schedule Week 2 to run immediately after Week 1 completes
        async_task(
            "apps.insights.tasks.process_week_task",
            file_path,
            week2_start_date.strftime("%Y-%m-%d"),
            2,
        )
        logger.info("Week 2 task scheduled successfully.")

    except Exception as e:
        logger.error(f"Failed to schedule two summaries: {e}")
        raise


# Example trigger:
# schedule_two_summaries("/path/to/ga4_data.csv", "2024-01-01")
