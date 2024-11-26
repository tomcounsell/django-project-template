# apps/insights/services/comparison_service.py
"""
Comparison Service for Dataset Summaries
Handles LLM comparison generation and logging for two dataset summaries.
"""

import json
import logging
from datetime import datetime, timedelta
from django.db import transaction
from apps.insights.models.comparison import Comparison, KeyMetricComparison
from apps.insights.models.summary import Summary
from apps.insights.services.openai.comparison_generator import generate_comparison
from apps.insights.services.openai.schemas import ComparisonOutput


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_comparison(start_date: str):
    """
    Fetches summaries for current week and past week from the database,
    passes them to the processing service, then saves the comparison to the database.

    """
    try:
        logger.info("Fetching summaries from the database...")
        start_date_week1 = datetime.strptime(start_date, "%Y-%m-%d")
        start_date_week2 = start_date_week1 - timedelta(days=7)

        # Fetch summaries
        summary1 = Summary.objects.get(start_date=start_date_week1.strftime("%Y-%m-%d"))
        summary2 = Summary.objects.get(start_date=start_date_week2.strftime("%Y-%m-%d"))

        logger.info(f"Current Week Summary ID: {summary1.id}")
        logger.info(f"Past Week Summary ID: {summary2.id}")

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
        logger.info(f"Comparison Summary: {comparison_result.comparison_summary}")
        for metric in comparison_result.key_metrics_comparison:
            logger.info(
                f"{metric.name}: Current Week = {metric.value1}, Past Week = {metric.value2} ({metric.description})"
            )

        # Save the comparison result to the database
        logger.info("Saving comparison result to the database...")
        save_comparison_to_database(summary1.id, summary2.id, comparison_result)
        logger.info("Comparison result has been saved successfully!")

    except Summary.DoesNotExist as e:
        logger.error(f"Summary not found: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")

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
        logging.debug(f"Prepared Summary of Current Week:\n{summary1}")
        logging.debug(f"Prepared Summary of Previous Week:\n{summary2}")

        # Step 2:Generate comparison using LLM
        comparison_result = generate_comparison(summary1, summary2)

        # Log detailed results
        logging.info("Comparison completed successfully.")
        logging.debug(f"Raw comparison result: {comparison_result}")

        logging.info("Comparison Summary:")
        logging.info(comparison_result.comparison_summary)
        logging.info("Key Metrics Comparison:")
        for metric in comparison_result.key_metrics_comparison:
            logging.info(
                f"{metric.name}: Current Week = {metric.value1}, Past Week = {metric.value2} ({metric.description})"
            )

        return comparison_result

    except ValueError as ve:
        logging.error(f"Validation error during comparison: {ve}")
        raise

    except Exception as e:
        logging.error(f"Unexpected error during comparison: {e}")
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
            f"- {metric['name']}: {metric['value']}"
            for metric in data_summary["key_metrics"]
            if "name" in metric and "value" in metric
        )

        if not key_metrics_str:
            logging.warning("Key metrics are empty or malformed.")
            key_metrics_str = "No key metrics available."

        return f"{data_summary['dataset_summary']}\n\nKey Metrics:\n{key_metrics_str}"
    except Exception as e:
        logging.error(f"Failed to prepare summary: {e}")
        raise


# def save_comparison_to_database(
#     summary1_id: int, summary2_id: int, comparison_result: ComparisonOutput
# ):
#     """
#     Save the LLM comparison result into the database.

#     Args:
#         summary1_id (int): ID of the first summary (Week 1).
#         summary2_id (int): ID of the second summary (Week 2).
#         comparison_result (ComparisonOutput): The structured comparison result from LLM.
#     """
#     try:
#         with transaction.atomic():
#             # Fetch the summaries
#             summary1 = Summary.objects.get(id=summary1_id)
#             summary2 = Summary.objects.get(id=summary2_id)

#             logging.info(
#                 f"Saving comparison for summaries {summary1_id} and {summary2_id}..."
#             )

#             # Create the Comparison object
#             comparison = Comparison.objects.create(
#                 summary1=summary1,
#                 summary2=summary2,
#                 comparison_summary=comparison_result.comparison_summary,
#             )

#             # Create KeyMetricComparison objects
#             for metric in comparison_result.key_metrics_comparison:
#                 KeyMetricComparison.objects.create(
#                     comparison=comparison,
#                     name=metric.name,
#                     value1=metric.value1,
#                     value2=metric.value2,
#                     description=metric.description,
#                 )

#             logging.info(
#                 f"Comparison saved successfully for summaries {summary1_id} and {summary2_id}."
#             )

#     except Summary.DoesNotExist as e:
#         logging.error(f"Summary not found: {e}")
#         raise ValueError(f"Summary not found: {e}")
#     except Exception as e:
#         logging.error(f"Failed to save comparison to the database: {e}")
#         raise
