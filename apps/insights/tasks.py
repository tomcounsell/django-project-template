# apps/insights/tasks.py
"""
Task definitions for the Insights app.
These tasks integrate with Django-Q to run asynchronously.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django_q.tasks import async_task, result_group, fetch
from django_q.models import OrmQ

import pandas as pd

from apps.insights.services.summary_service import process_week
from apps.insights.services.comparison_service import (
    process_comparison,
)  # Corrected import
from apps.insights.services.openai.schemas import SummaryOutput, ComparisonOutput

logger = logging.getLogger(__name__)


def process_week_task(file_path: str, start_date: str, week: int) -> SummaryOutput:
    """
    Processes a single week's data and generates an LLM summary.

    Args:
        file_path (str): Path to the CSV file.
        start_date (str): Start date for the week (YYYY-MM-DD).
        week (int): Week number (1 or 2).

    Returns:
        SummaryOutput: The summary output for the week.
    """
    try:
        logger.info(f"Processing Week {week} starting from {start_date}...")
        result = process_week(file_path, start_date, week)
        logger.info(f"Week {week} summary generated successfully.")
        return result  # Returning the SummaryOutput object directly
    except Exception as e:
        logger.error(f"Failed to process Week {week}: {e}")
        raise


def compare_summaries_task(
    week1_summary: SummaryOutput, week2_summary: SummaryOutput
) -> ComparisonOutput:
    """
    Compares two LLM-generated summaries and generates a comparative analysis.

    Args:
        week1_summary (SummaryOutput): Week 1 summary.
        week2_summary (SummaryOutput): Week 2 summary.

    Returns:
        ComparisonOutput: The comparison output.
    """
    try:
        logger.info("Generating comparison between Week 1 and Week 2 summaries...")
        # Convert SummaryOutput objects to dicts for process_comparison
        summary1_dict = week1_summary.dict()
        summary2_dict = week2_summary.dict()

        comparison_result = process_comparison(summary1_dict, summary2_dict)
        logger.info("Comparison generated successfully.")
        return comparison_result
    except Exception as e:
        logger.error(f"Failed to generate comparison: {e}")
        raise


def schedule_tasks(file_path: str, start_date: str):
    """
    Schedules tasks to process Week 1 and Week 2 sequentially and then compare them.
    """
    try:
        logger.info("Scheduling tasks for Week 1, Week 2, and comparison...")

        # Calculate Week 2 start date
        week2_start_date = pd.to_datetime(start_date) + pd.Timedelta(days=7)
        week2_start_date_str = week2_start_date.strftime("%Y-%m-%d")

        # Schedule Week 1 task with a chain
        async_task(
            "apps.insights.tasks.process_week_task",
            file_path,
            start_date,
            1,
            group="process_summaries",
            hook="apps.insights.tasks.week1_completed_hook",
            kwargs={
                "file_path": file_path,
                "week2_start_date_str": week2_start_date_str,
            },
        )

        logger.info("Tasks scheduled successfully.")

    except Exception as e:
        logger.error(f"Failed to schedule tasks: {e}")
        raise


def week1_completed_hook(task_result, file_path: str, week2_start_date_str: str):
    """
    Hook function called after Week 1 task completes.
    Schedules Week 2 task.

    Args:
        task_result (SummaryOutput): Result from Week 1 processing.
        file_path (str): Path to the CSV file.
        week2_start_date_str (str): Start date for Week 2.
    """
    try:
        logger.info("Week 1 processing completed. Scheduling Week 2 task...")
        # Save Week 1 result to the database or cache if needed
        week1_summary = task_result  # SummaryOutput object

        # Schedule Week 2 task with a hook to run the comparison after completion
        async_task(
            "apps.insights.tasks.process_week_task",
            file_path,
            week2_start_date_str,
            2,
            hook="apps.insights.tasks.week2_completed_hook",
            kwargs={
                "week1_summary": week1_summary,
            },
        )
        logger.info("Week 2 task scheduled successfully.")
    except Exception as e:
        logger.error(f"Failed in week1_completed_hook: {e}")
        raise


def week2_completed_hook(task_result, week1_summary: SummaryOutput):
    """
    Hook function called after Week 2 task completes.
    Runs the comparison task.

    Args:
        task_result (SummaryOutput): Result from Week 2 processing.
        week1_summary (SummaryOutput): Result from Week 1 processing.
    """
    try:
        logger.info("Week 2 processing completed. Running comparison task...")
        week2_summary = task_result  # SummaryOutput object

        # Run comparison task
        comparison_result = compare_summaries_task(week1_summary, week2_summary)

        # Optionally, save comparison_result to the database or handle as needed
        logger.info("Comparison task completed successfully.")
    except Exception as e:
        logger.error(f"Failed in week2_completed_hook: {e}")
        raise
