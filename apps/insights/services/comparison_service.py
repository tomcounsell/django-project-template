# apps/insights/services/comparison_service.py
"""
Comparison Service for Dataset Summaries
Handles LLM comparison generation and logging for two dataset summaries.
"""

import logging
from apps.insights.services.openai.comparison_generator import generate_comparison
from apps.insights.services.openai.schemas import ComparisonOutput

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def prepare_summary(data_summary):
    """
    Combines dataset_summary and key_metrics from a structured dataset summary into a single string for LLM input.

    Args:
        data_summary (dict): A dictionary containing 'dataset_summary' (str) and 'key_metrics' (list of dicts).

    Returns:
        str: A combined string representation of the dataset summary and its key metrics.
    """
    key_metrics_str = "\n".join(
        f"- {metric['name']}: {metric['value']} ({metric['description']})"
        for metric in data_summary["key_metrics"]
    )
    return f"{data_summary['dataset_summary']}\n\nKey Metrics:\n{key_metrics_str}"


def process_comparison(data_summary1, data_summary2) -> ComparisonOutput:
    """
    Processes two dataset summaries, merges them into strings, and generates a structured comparison.

    Args:
        data_summary1 (dict): The first dataset summary (with 'dataset_summary' and 'key_metrics').
        data_summary2 (dict): The second dataset summary.

    Returns:
        ComparisonOutput: A structured comparison containing a summary,
                          key metrics comparison, and notable trends.
    """
    try:
        logging.info("Starting comparison of dataset summaries...")

        # Prepare text strings for the LLM
        summary1 = prepare_summary(data_summary1)
        summary2 = prepare_summary(data_summary2)

        # Generate comparison using LLM
        comparison_result = generate_comparison(summary1, summary2)

        # Log results
        logging.info("Comparison Summary:")
        logging.info(comparison_result.comparison_summary)
        logging.info("Key Metrics Comparison:")
        for metric in comparison_result.key_metrics_comparison:
            logging.info(
                f"{metric.name}: Week 1 Value = {metric.value1}, "
                f"Week 2 Value = {metric.value2} ({metric.description})"
            )
        if comparison_result.notable_trends:
            logging.info(f"Notable Trends: {comparison_result.notable_trends}")
        else:
            logging.info("No notable trends identified.")

        return comparison_result

    except Exception as e:
        logging.error(f"Failed to process dataset comparison: {e}")
        raise
