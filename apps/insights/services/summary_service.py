# apps/insights/services/summary_service.py
"""
Summary Service for Single-Week Data Processing
Handles CSV data validation, processing, LLM summary generation, and key metric extraction for a single week.

This service processes a single week's data from a CSV file, generating a summary and key metrics using OpenAI's LLM, and saving the results to both the database and a JSON file. It uses the CSVProcessor to load, validate, clean, and filter data based on the provided start date. A statistical overview is generated for the specified week, which is then summarized into a dataset summary and key metrics. The results are stored in the Summary and KeyMetric models and saved as JSON for debugging or visualization. Errors are logged at each step.

"""

import json
import logging
from django.db import transaction
from apps.insights.models.summary import Summary, KeyMetric
from apps.insights.services.csv_processor import CSVProcessor
from apps.insights.services.openai.summary_generator import generate_summary
from apps.insights.services.openai.schemas import SummaryOutput
import pandas as pd
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def process_week(start_date: str, week_number: int) -> SummaryOutput:
    """
    Processes a single week's data and generates an LLM summary.

    Args:
        start_date (str): Start date for the dataset (YYYY-MM-DD).
        week_number (int): Week number to process (1 = days 1-7, 2 = days 8-14).

    Returns:
        SummaryOutput: LLM summary and key metrics for the week.
    """
    try:
        logging.info(f"Processing Week {week_number} starting from {start_date}...")

        # Initialize CSVProcessor and load data
        processor = CSVProcessor()
        processor.load()
        processor.validate()
        processor.clean()

        # Filter data for the specified week
        week_df = processor.filter(start_date, week_number)

        if week_df.empty:
            raise ValueError(f"No data found for Week {week_number}.")

        # Generate statistical overview and LLM summary
        processor.generate_overview(week_df, f"Week {week_number}")
        statistical_summary = week_df.describe().to_string()
        llm_summary = generate_summary(statistical_summary)

        # Determine end date for the week
        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = start_date_dt + pd.Timedelta(days=(7 * week_number - 1))
        start_date_formatted = start_date_dt.strftime("%Y-%m-%d")
        end_date_formatted = end_date_dt.strftime("%Y-%m-%d")

        # Save summary to database and JSON
        save_summary_to_database(start_date_formatted, end_date_formatted, llm_summary)
        save_summary_to_file(start_date_formatted, end_date_formatted, llm_summary)

        return llm_summary
    except Exception as e:
        logging.error(f"Failed to process Week {week_number}: {e}")
        raise


def save_summary_to_database(
    start_date: str, end_date: str, llm_summary: SummaryOutput
):
    """
    Saves the structured summary result and its key metrics to the database.

    Args:
        start_date (str): Start date for the summary (YYYY-MM-DD).
        end_date (str): End date for the summary (YYYY-MM-DD).
        llm_summary (SummaryOutput): The structured summary result.
    """
    try:
        with transaction.atomic():
            logging.info(
                f"Saving summary for {start_date} to {end_date} to the database..."
            )

            summary = Summary.objects.create(
                start_date=start_date,
                end_date=end_date,
                dataset_summary=llm_summary.dataset_summary,
            )

            for metric in llm_summary.key_metrics:
                KeyMetric.objects.create(
                    summary=summary,
                    name=metric.name,
                    value=metric.value,
                )

            logging.info(
                f"Summary and key metrics for {start_date} to {end_date} saved successfully."
            )

    except Exception as e:
        logging.error(f"Failed to save summary and key metrics to the database: {e}")
        raise


def save_summary_to_file(start_date: str, end_date: str, llm_summary: SummaryOutput):
    """
    Saves the structured summary result to a JSON file in the same format as the database.

    Args:
        start_date (str): Start date for the summary (YYYY-MM-DD).
        end_date (str): End date for the summary (YYYY-MM-DD).
        llm_summary (SummaryOutput): The structured summary result.
    """
    try:
        file_path = f"summary_output_{start_date}_to_{end_date}.json"
        logging.info(f"Saving summary result to {file_path}...")

        data = {
            "start_date": start_date,
            "end_date": end_date,
            "dataset_summary": llm_summary.dataset_summary,
            "key_metrics": [
                {"name": metric.name, "value": metric.value}
                for metric in llm_summary.key_metrics
            ],
        }

        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        logging.info("Summary result saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save summary result to file: {e}")
        raise
