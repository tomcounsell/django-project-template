# apps/insights/services/comparison_task_service.py

from apps.insights.models.summary import Summary
from apps.insights.services.openai.comparison_generator import generate_comparison
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def run_comparison_task(start_date: str) -> dict:
    """
    Fetch summaries for Week 1 and Week 2 from the database, then pass them to the comparison service.

    Args:
        start_date (str): Start date for Week 1 in the format 'YYYY-MM-DD'.

    Returns:
        dict: The result of the comparison service.
    """
    try:
        logger.info(f"Running comparison task for start_date: {start_date}")

        # Convert start_date to datetime
        start_date_week1 = datetime.strptime(start_date, "%Y-%m-%d")
        start_date_week2 = start_date_week1 + timedelta(days=7)

        # Fetch summaries
        logger.info("Fetching summaries from the database...")
        summary1 = Summary.objects.get(
            start_date=start_date_week1.strftime("%Y-%m-%d")
        ).dataset_summary
        summary2 = Summary.objects.get(
            start_date=start_date_week2.strftime("%Y-%m-%d")
        ).dataset_summary

        logger.info("Summaries fetched successfully.")
        logger.info(
            f"Week 1 Summary: {summary1[:50]}..."
        )  # Log a snippet of the summary
        logger.info(
            f"Week 2 Summary: {summary2[:50]}..."
        )  # Log a snippet of the summary

        # Pass summaries to the comparison generator
        logger.info("Generating comparison...")
        comparison_result = generate_comparison(summary1, summary2)

        logger.info("Comparison generated successfully!")
        return comparison_result

    except Summary.DoesNotExist as e:
        logger.error(f"Summary not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while running comparison task: {e}")
        raise
