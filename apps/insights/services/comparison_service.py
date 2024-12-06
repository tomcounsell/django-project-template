# apps/insights/services/comparison_service.py
"""
Comparison Service for Dataset Summaries
Handles LLM comparison generation for two dataset summaries stored in the database.

This service compares dataset summaries and key metrics for the current and previous weeks using OpenAI's LLM. It begins by validating the absence of duplicate comparisons, then fetches the relevant summaries from the database. The summaries are formatted and processed to generate a natural language comparison summary and key metrics comparison. Results are stored in the Comparison and KeyMetricComparison models, ensuring persistence and availability for further analysis. Errors are logged at each step to facilitate debugging and maintain reliability.
"""

import logging
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from apps.insights.models.comparison import Comparison, KeyMetricComparison
from apps.insights.models.summary import Summary
from apps.insights.services.openai.comparison_generator import generate_comparison
from apps.insights.services.openai.schemas import ComparisonOutput
from apps.insights.services.utils.db_operations import save_comparison_to_database

logger = logging.getLogger(__name__)


def create_comparison(start_date: str):
    """
    Fetches summaries for current week and past week from the database,
    passes them to the processing service, then saves the comparison to the database.

    Args:
        start_date (str): The start date for the current week's summary (YYYY-MM-DD).

    Raises:
        ValidationError: Raised if one or both summaries are missing, or if a comparison already exists.
    """
    try:
        logger.info("Starting comparison creation process...")

        # Calculate start dates for the two weeks
        start_date_week1 = datetime.strptime(start_date, "%Y-%m-%d")
        start_date_week2 = start_date_week1 - timedelta(days=7)
        logger.info(
            "Start dates - Current Week: %s, Previous Week: %s",
            start_date_week1,
            start_date_week2,
        )

        # Check if a comparison already exists
        logger.info("Checking for an existing comparison...")
        if Comparison.objects.filter(
            summary1__start_date=start_date_week1.strftime("%Y-%m-%d"),
            summary2__start_date=start_date_week2.strftime("%Y-%m-%d"),
        ).exists():
            logger.error(
                "A comparison already exists for summaries with start dates %s and %s.",
                start_date_week1.strftime("%Y-%m-%d"),
                start_date_week2.strftime("%Y-%m-%d"),
            )
            raise ValidationError(
                "A comparison already exists for the given summaries."
            )

        # Fetch summaries for both weeks
        try:
            summary1 = Summary.objects.get(
                start_date=start_date_week1.strftime("%Y-%m-%d")
            )
            logger.info("Found Current Week Summary ID: %s", summary1.id)
        except Summary.DoesNotExist as exc:
            logger.error(
                "Summary for Current Week (%s) not found.",
                start_date_week1.strftime("%Y-%m-%d"),
            )
            raise ValidationError(f"Summary for the week beginning ({start_date_week1.strftime('%Y-%m-%d')}) does not exist.") from exc

        try:
            summary2 = Summary.objects.get(
                start_date=start_date_week2.strftime("%Y-%m-%d")
            )
            logger.info("Found Past Week Summary ID: %s", summary2.id)
        except Summary.DoesNotExist as exc:
            logger.error(
                "Summary for Past Week (%s) not found.",
                start_date_week2.strftime("%Y-%m-%d"),
            )
            raise ValidationError(f"Summary for the week prior to ({start_date_week2.strftime('%Y-%m-%d')}) does not exist.") from exc

        # Run the comparison service
        logger.info("Running comparison service...")
        data_summary1 = {
            "dataset_summary": summary1.dataset_summary,
            "key_metrics": [
                {"name": metric.name, "value": metric.value}
                for metric in summary1.key_metrics.all()
            ],
        }
        data_summary2 = {
            "dataset_summary": summary2.dataset_summary,
            "key_metrics": [
                {"name": metric.name, "value": metric.value}
                for metric in summary2.key_metrics.all()
            ],
        }

        comparison_result = process_summaries(data_summary1, data_summary2)

        # Log the comparison result
        logger.info("Comparison Service Output:")
        logger.info("Comparison Summary: %s", comparison_result.comparison_summary)
        for metric in comparison_result.key_metrics_comparison:
            logger.info(
                "%s: Current Week = %s, Past Week = %s (%s)",
                metric.name,
                metric.value1,
                metric.value2,
                metric.description,
            )

        # Save the comparison result to the database
        logger.info("Saving comparison result to the database...")
        save_comparison_to_database(summary1.id, summary2.id, comparison_result)
        logger.info("Comparison result has been saved successfully!")

    except ValidationError as ve:
        logger.error("Validation error: %s", ve)
        raise
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise RuntimeError("Failed to create comparison.") from e

    logger.info("Comparison generation completed.")


def process_summaries(data_summary1: dict, data_summary2: dict) -> ComparisonOutput:
    """
    Merges two dataset summaries into strings and generates a structured comparison.

    Args:
        data_summary1 (dict): The first dataset summary with 'key_metrics'.
        data_summary2 (dict): The second dataset summary with 'key_metrics'.

    Returns:
        ComparisonOutput: A structured comparison containing a summary and key metrics comparison.
    """
    try:
        logging.info("Starting comparison of dataset summaries...")

        # Step 1: Validate and prepare text strings for the LLM
        summary1 = format_summary(data_summary1)
        summary2 = format_summary(data_summary2)

        logging.info("Generated summaries for comparison.")
        logging.debug("Prepared Summary of Current Week:\n%s", summary1)
        logging.debug("Prepared Summary of Previous Week:\n%s", summary2)

        # Step 2:Generate comparison using LLM
        comparison_result = generate_comparison(summary1, summary2)

        # Log detailed results
        logging.info("Comparison completed successfully.")
        logging.debug("Raw comparison result: %s", comparison_result)

        logging.info("Comparison Summary:")
        logging.info("%s", comparison_result.comparison_summary)
        logging.info("Key Metrics Comparison:")
        for metric in comparison_result.key_metrics_comparison:
            logging.info(
                "%s: Current Week = %s, Past Week = %s (%s)",
                metric.name,
                metric.value1,
                metric.value2,
                metric.description,
            )

        return comparison_result

    except ValueError as ve:
        logging.error("Validation error during comparison: %s", ve)
        raise

    except Exception as e:
        logging.error("Unexpected error during comparison: %s", e)
        raise


def format_summary(data_summary: dict) -> str:
    """
    Combines dataset_summary and key_metrics from a structured dataset summary into a single string for LLM input.

    Args:
        data_summary (dict): A dictionary containing 'dataset_summary' (str) and 'key_metrics' (list of dicts).

    Returns:
        str: A combined string representation of the dataset summary and its key metrics.
    """
    try:
        if not isinstance(data_summary, dict):
            raise ValueError("data_summary must be a dictionary.")

        if not data_summary.get("dataset_summary"):
            raise ValueError("Missing 'dataset_summary' in data_summary.")

        if not data_summary.get("key_metrics"):
            raise ValueError("Missing 'key_metrics' in data_summary.")

        key_metrics_str = "\n".join(
            "- %s: %s" % (metric["name"], metric["value"])
            for metric in data_summary["key_metrics"]
            if "name" in metric and "value" in metric
        )

        if not key_metrics_str:
            logging.warning("Key metrics are empty or malformed.")
            key_metrics_str = "No key metrics available."

        return "%s\n\nKey Metrics:\n%s" % (
            data_summary["dataset_summary"],
            key_metrics_str,
        )
    except Exception as e:
        logging.error("Failed to prepare summary: %s", e)
        raise
