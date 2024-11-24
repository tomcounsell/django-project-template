# apps/insights/services/comparison_service.py
"""
Comparison Service for Dataset Summaries
Handles LLM comparison generation and logging for two dataset summaries.
"""

import json
import logging
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
        if not data_summary.get("dataset_summary"):
            raise ValueError("Missing 'dataset_summary' in data_summary.")

        if not data_summary.get("key_metrics"):
            raise ValueError("Missing 'key_metrics' in data_summary.")

        key_metrics_str = "\n".join(
            f"- {metric['name']}: {metric['value']} ({metric['description']})"
            for metric in data_summary["key_metrics"]
            if "name" in metric and "value" in metric and "description" in metric
        )

        if not key_metrics_str:
            logging.warning("Key metrics are empty or malformed.")

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
        logging.debug(f"Summary 1: {summary1}")
        logging.debug(f"Summary 2: {summary2}")

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
                f"{metric.name}: Week 1 Value = {metric.value1}, "
                f"Week 2 Value = {metric.value2} ({metric.description})"
            )

        # Removed handling of 'notable_trends' as it no longer exists
        # Save comparison result to JSON file
        save_comparison_to_file(comparison_result)

        return comparison_result

    except ValueError as ve:
        logging.error(f"Validation Error: {ve}")
        raise

    except Exception as e:
        logging.error(f"Unexpected error during comparison: {e}")
        raise


def save_comparison_to_file(comparison_result: ComparisonOutput):
    """
    Saves the structured comparison result to a JSON file.

    Args:
        comparison_result (ComparisonOutput): The structured comparison result.
    """
    try:
        file_path = "comparison_output.json"
        logging.info(f"Saving comparison result to {file_path}...")
        with open(file_path, "w") as json_file:
            json.dump(comparison_result.dict(), json_file, indent=4)
        logging.info("Comparison result saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save comparison result to file: {e}")
        raise
