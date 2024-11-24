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
import datetime  # Added import for datetime

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

        # Verify the 'date' column type
        if not pd.api.types.is_datetime64_any_dtype(processor.df["date"]):
            logging.error("The 'date' column is not in datetime format after cleaning.")
            raise TypeError("Date column is not datetime")

        # Filter data for the specified week
        week_df = processor.filter(start_date)[week_number - 1]

        # Verify the 'date' column type in week_df
        if not pd.api.types.is_datetime64_any_dtype(week_df["date"]):
            logging.error("The 'date' column in week_df is not in datetime format.")
            raise TypeError("Date column in week_df is not datetime")

        # Generate statistical overview using CSVProcessor
        processor.generate_overview(week_df, f"Week {week_number}")

        # Generate LLM summary
        logging.info("Requesting summary from OpenAI...")
        statistical_summary = week_df.describe().to_string()
        llm_summary = generate_summary(statistical_summary)

        # Validate and log results
        logging.info(f"LLM Summary - Week {week_number}: {llm_summary.dataset_summary}")
        logging.info("Key Metrics:")
        for metric in llm_summary.key_metrics:
            logging.info(f"{metric.name}: {metric.value}")

        # Convert `date` column to datetime and extract the end date
        end_date_max = week_df["date"].max()
        logging.info(f"Max date value: {end_date_max} (type: {type(end_date_max)})")
        if isinstance(end_date_max, (pd.Timestamp, datetime.datetime)):
            end_date = end_date_max.strftime("%Y-%m-%d")
        else:
            # Attempt to convert to datetime if not already
            end_date = pd.to_datetime(end_date_max).strftime("%Y-%m-%d")

        # Save summary and metrics to the database
        save_summary_to_database(
            start_date=start_date,
            end_date=end_date,
            llm_summary=llm_summary,
        )

        # Save summary to JSON file
        save_summary_to_file(start_date, end_date, llm_summary, week_number)

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
        with transaction.atomic():  # Ensure all-or-nothing database operations
            logging.info(
                f"Saving summary for {start_date} to {end_date} to the database..."
            )

            # Create and save the Summary instance
            summary = Summary.objects.create(
                start_date=start_date,
                end_date=end_date,
                dataset_summary=llm_summary.dataset_summary,
            )

            # Create and save the KeyMetric instances
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


def save_summary_to_file(
    start_date: str, end_date: str, llm_summary: SummaryOutput, week_number: int
):
    """
    Saves the structured summary result to a JSON file in the same format as the database.

    Args:
        start_date (str): Start date for the summary (YYYY-MM-DD).
        end_date (str): End date for the summary (YYYY-MM-DD).
        llm_summary (SummaryOutput): The structured summary result.
        week_number (int): The week number being processed.
    """
    try:
        file_path = f"summary_output_week_{week_number}.json"
        logging.info(f"Saving Week {week_number} summary result to {file_path}...")

        # Construct the data dictionary to match database structure
        data = {
            "start_date": start_date,
            "end_date": end_date,
            "dataset_summary": llm_summary.dataset_summary,
            "key_metrics": [
                {"name": metric.name, "value": metric.value}
                for metric in llm_summary.key_metrics
            ],
        }

        # Write to the JSON file
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        logging.info(f"Week {week_number} summary result saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save Week {week_number} summary result to file: {e}")
        raise
