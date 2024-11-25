# apps/insights/services/comparison_service.py
"""
Comparison Service for Dataset Summaries
Handles LLM comparison generation and logging for two dataset summaries.
"""

import json
import logging
from django.db import transaction
from apps.insights.models.comparison import Comparison, KeyMetricComparison
from apps.insights.models.summary import Summary
from apps.insights.services.openai.comparison_generator import generate_comparison
from apps.insights.services.openai.schemas import ComparisonOutput


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def prepare_summary(data_summary: dict) -> str:
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


def process_comparison(data_summary1: dict, data_summary2: dict) -> ComparisonOutput:
    """
    Processes two dataset summaries, merges them into strings, and generates a structured comparison.

    Args:
        data_summary1 (dict): The first dataset summary (with 'dataset_summary' and 'key_metrics').
        data_summary2 (dict): The second dataset summary.

    Returns:
        ComparisonOutput: A structured comparison containing a summary and key metrics comparison.
    """
    try:
        logging.info("Starting comparison of dataset summaries...")

        # Validate and prepare text strings for the LLM
        summary1 = prepare_summary(data_summary1)
        summary2 = prepare_summary(data_summary2)

        logging.info("Generated summaries for comparison.")
        logging.debug(f"Prepared Summary 1:\n{summary1}")
        logging.debug(f"Prepared Summary 2:\n{summary2}")

        # Generate comparison using LLM
        comparison_result = generate_comparison(summary1, summary2)

        # Log detailed results
        logging.info("Comparison completed successfully.")
        logging.debug(f"Raw comparison result: {comparison_result}")

        logging.info("Comparison Summary:")
        logging.info(comparison_result.comparison_summary)
        logging.info("Key Metrics Comparison:")
        for metric in comparison_result.key_metrics_comparison:
            logging.info(
                f"{metric.name}: Week 1 = {metric.value1}, Week 2 = {metric.value2} ({metric.description})"
            )

        return comparison_result

    except ValueError as ve:
        logging.error(f"Validation Error during comparison: {ve}")
        raise

    except Exception as e:
        logging.error(f"Unexpected error during comparison: {e}")
        raise


def save_comparison_to_database(
    summary1_id: int, summary2_id: int, comparison_result: ComparisonOutput
):
    """
    Save the LLM comparison result into the database.

    Args:
        summary1_id (int): ID of the first summary (Week 1).
        summary2_id (int): ID of the second summary (Week 2).
        comparison_result (ComparisonOutput): The structured comparison result from LLM.
    """
    try:
        with transaction.atomic():
            # Fetch the summaries
            summary1 = Summary.objects.get(id=summary1_id)
            summary2 = Summary.objects.get(id=summary2_id)

            logging.info(
                f"Saving comparison for summaries {summary1_id} and {summary2_id}..."
            )

            # Create the Comparison object
            comparison = Comparison.objects.create(
                summary1=summary1,
                summary2=summary2,
                comparison_summary=comparison_result.comparison_summary,
            )

            # Create KeyMetricComparison objects
            for metric in comparison_result.key_metrics_comparison:
                KeyMetricComparison.objects.create(
                    comparison=comparison,
                    name=metric.name,
                    value1=metric.value1,
                    value2=metric.value2,
                    description=metric.description,
                )

            logging.info(
                f"Comparison saved successfully for summaries {summary1_id} and {summary2_id}."
            )

    except Summary.DoesNotExist as e:
        logging.error(f"Summary not found: {e}")
        raise ValueError(f"Summary not found: {e}")
    except Exception as e:
        logging.error(f"Failed to save comparison to the database: {e}")
        raise
