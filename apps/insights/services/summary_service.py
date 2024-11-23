# apps/insights/services/summary_service.py
"""
Summary Service for Single-Week Data Processing
Handles CSV data validation, processing, LLM summary generation, and key metric extraction for a single week.
"""

import logging
import pandas as pd
from apps.insights.services.csv_processor import CSVProcessor
from apps.insights.services.openai.summary_generator import generate_summary
from apps.insights.services.openai.schemas import SummaryOutput

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_week(file_path: str, start_date: str, week_number: int) -> SummaryOutput:
    """
    Processes a single week's data and generates an LLM summary.

    Args:
        file_path (str): Path to the CSV file.
        start_date (str): Start date for the week (YYYY-MM-DD).
        week_number (int): Week number (1 or 2).

    Returns:
        SummaryOutput: LLM summary and key metrics for the week.
    """
    try:
        logging.info(
            f"Processing Week {week_number} data starting from {start_date}..."
        )

        # Initialize CSVProcessor and load data
        processor = CSVProcessor(file_path)
        processor.load()
        processor.validate()
        processor.clean()

        # Filter data for the specified week
        week_df = processor.filter(start_date)[week_number - 1]

        # Log statistical overview
        logging.info(f"Statistical Overview - Week {week_number}:")
        print(week_df.describe().to_string())

        # Generate LLM summary
        logging.info("Requesting summary from OpenAI...")
        statistical_summary = week_df.describe().to_string()
        llm_summary = generate_summary(statistical_summary)

        # Validate and log results
        logging.info(f"LLM Summary - Week {week_number}: {llm_summary.dataset_summary}")
        logging.info("Key Metrics:")
        for metric in llm_summary.key_metrics:
            logging.info(f"{metric.name}: {metric.value} ({metric.description})")

        return llm_summary

    except Exception as e:
        logging.error(f"Failed to process Week {week_number}: {e}")
        raise