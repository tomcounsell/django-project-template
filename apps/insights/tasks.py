# apps/insights/tasks.py
"""
Task definitions for the Insights app.
These tasks integrate with Django-Q to run asynchronously.
"""

import logging
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


# Example trigger:
# async_task("apps.insights.tasks.run_pipeline_task", "/path/to/ga4_data.csv", "2024-01-01")
