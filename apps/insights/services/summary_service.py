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
            "Starting process_week: start_date=%s, week_number=%s",
            start_date,
            week_number,
        )

        # Convert start_date to datetime
        start_date_dt = pd.to_datetime(start_date)

        # Adjust start_date for Week 2 task
        if week_number == 2:
            start_date_dt -= pd.Timedelta(days=7)

        # Date to use for validation and processing
        adjusted_start_date_str = start_date_dt.strftime("%Y-%m-%d")

        # Validate that start_date is in the past
        if start_date_dt > pd.Timestamp.now():
            logging.error(
                "Validation failed: Start date %s cannot be in the future.",
                adjusted_start_date_str,
            )
            raise ValidationError(
                "Start date %s cannot be in the future." % adjusted_start_date_str
            )

        # Validate uniqueness of start_date
        if Summary.objects.filter(start_date=adjusted_start_date_str).exists():
            logging.error(
                "Duplicate summary found for start_date: %s", adjusted_start_date_str
            )
            raise ValidationError(
                "A summary for the start date %s already exists."
                % adjusted_start_date_str
            )

        # Step 1: Initialize CSVProcessor and load data
        logging.info("Initializing CSVProcessor...")
        processor = CSVProcessor()

        logging.info("Loading CSV...")
        processor.load()
        logging.info("CSV loaded successfully.")

        # Step 2: Validate
        logging.info("Validating CSV...")
        processor.validate()
        logging.info("Validation complete.")

        # Step 3: Clean
        logging.info("Cleaning CSV...")
        processor.clean()
        logging.info("Cleaning complete.")

        # Step 4: Filter data
        logging.info("Filtering data for week: %s", week_number)
        week_df = processor.filter(adjusted_start_date_str)
        if week_df.empty:
            raise ValidationError(
                f"No data available for the specified week starting on {adjusted_start_date_str}."
            )
        logging.info("Filtering complete. Filtered rows: %s", len(week_df))

        # Step 5: Generate statistical overview
        processor.df = week_df  # Update self.df with the filtered DataFrame
        logging.info("Generating statistical overview...")
        statistical_summary = processor.generate_overview()

        # Step 6: Generate LLM summary
        logging.info("Calling LLM to generate summary...")

        llm_summary = generate_summary(statistical_summary)
        logging.info("LLM summary generated successfully.")

        # Step 7: Save results to database
        logging.info("Saving results to database...")
        save_summary_to_database(
            adjusted_start_date_str,
            llm_summary,
        )

    except ValidationError as ve:
        logging.error("Validation error: %s", ve)
        raise
    except Exception as e:
        logging.error("Error in process_week: %s", e)
        raise

    return {
        "dataset_summary": llm_summary.dataset_summary,
        "key_metrics": llm_summary.key_metrics,
    }
