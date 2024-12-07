# app/insights/services/summary_service.py
"""
Summary Service for Single-Week Data Processing
Handles CSV data processing, summary generation, and key metric extraction for a single week.

This service processes a single week's data from a CSV file, generating a summary and key metrics using OpenAI's LLM, and saving the results to both the database and a JSON file. It uses the CSVProcessor to load, validate, clean, and filter data based on the provided start date. A statistical overview is generated for the specified week, which is then summarized into a dataset summary and key metrics. The results are stored in the Summary and KeyMetric models and saved as JSON for debugging or visualization. Errors are logged at each step.

"""
import logging
from django.core.exceptions import ValidationError
import pandas as pd
from apps.insights.models.summary import Summary
from apps.insights.services.csv.csv_processor import CSVProcessor
from apps.insights.services.openai.summary_generator import generate_summary
from apps.insights.services.utils.db_operations import save_summary_to_database

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def create_summary(start_date: str, week_number: int) -> dict:
    """
    Processes a single week's data and generates an LLM summary.

    Args:
        start_date (str): Start date for the dataset (YYYY-MM-DD).
        week_number (int): Week number to process (1 = current week, 2 = previous week).

    Returns:
        dict: JSON-serializable dictionary containing dataset_summary and key metrics.
    """
    try:
        logging.info(
            "Starting summary creation: start_date=%s, week_number=%s",
            start_date,
            week_number,
        )

        # Adjust and validate start_date
        start_date_dt = pd.to_datetime(start_date)
        if week_number == 2:
            start_date_dt -= pd.Timedelta(days=7)
        adjusted_start_date_str = start_date_dt.strftime("%Y-%m-%d")

        if start_date_dt > pd.Timestamp.now():
            raise ValidationError(
                f"Start date {adjusted_start_date_str} cannot be in the future."
            )

        if Summary.objects.filter(start_date=adjusted_start_date_str).exists():
            raise ValidationError(
                f"A summary for the start date {adjusted_start_date_str} already exists."
            )

        # Initialize and process dataset
        logging.info("Initializing and processing dataset...")
        processor = CSVProcessor()
        processor.load()
        processor.validate()
        processor.clean()
        week_df = processor.filter(adjusted_start_date_str)

        if week_df.empty:
            raise ValidationError(
                f"No data available for the specified week starting on {adjusted_start_date_str}."
            )

        # Generate overview and LLM summary
        processor.df = week_df
        statistical_summary = processor.generate_overview()
        logging.info("Generating LLM summary...")
        llm_summary = generate_summary(statistical_summary)

        # Save results to database
        logging.info("Saving summary to database...")
        save_summary_to_database(adjusted_start_date_str, llm_summary)

    except ValidationError as ve:
        logging.error("Validation error: %s", ve)
        raise
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        raise

    return {
        "dataset_summary": llm_summary.dataset_summary,
        "key_metrics": llm_summary.key_metrics,
    }
