# app/insights/services/summary_service.py
"""
Summary Service for Single-Week Data Processing
Handles CSV data validation, processing, LLM summary generation, and key metric extraction for a single week.

This service processes a single week's data from a CSV file, generating a summary and key metrics using OpenAI's LLM, and saving the results to both the database and a JSON file. It uses the CSVProcessor to load, validate, clean, and filter data based on the provided start date. A statistical overview is generated for the specified week, which is then summarized into a dataset summary and key metrics. The results are stored in the Summary and KeyMetric models and saved as JSON for debugging or visualization. Errors are logged at each step.

"""
import json
import logging
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from apps.insights.models.summary import Summary, KeyMetric
from apps.insights.services.csv_processor import CSVProcessor
from apps.insights.services.openai.summary_generator import generate_summary
from apps.insights.services.openai.schemas import SummaryOutput
import pandas as pd

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
            f"Starting process_week: start_date={start_date}, week_number={week_number}"
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
                f"Validation failed: Start date {adjusted_start_date_str} cannot be in the future."
            )
            raise ValidationError(
                f"Start date {adjusted_start_date_str} cannot be in the future."
            )

        # Validate uniqueness of start_date
        if Summary.objects.filter(start_date=adjusted_start_date_str).exists():
            logging.error(
                f"Duplicate summary found for start_date: {adjusted_start_date_str}"
            )
            raise ValidationError(
                f"A summary for the start date {adjusted_start_date_str} already exists."
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
        logging.info(f"Filtering data for week: {week_number}")
        week_df = processor.filter(adjusted_start_date_str)
        if week_df.empty:
            raise ValidationError(
                f"No data available for the specified week starting on {adjusted_start_date_str}."
            )
        logging.info(f"Filtering complete. Filtered rows: {len(week_df)}")

        # Step 5: Generate statistical overview
        logging.info("Generating statistical overview...")
        processor.generate_overview(week_df, f"Week {week_number}")

        # Step 6: Generate LLM summary
        logging.info("Calling LLM to generate summary...")
        statistical_summary = week_df.describe().to_string()
        llm_summary = generate_summary(statistical_summary)
        logging.info("LLM summary generated successfully.")

        # Step 7: Save results to database
        logging.info("Saving results to database...")
        save_summary_to_database(
            adjusted_start_date_str,
            llm_summary,
        )

        # Step 8: Prepare JSON-serializable output
        output = {
            "dataset_summary": llm_summary.dataset_summary,  # This is the string needed for comparison_service
            "key_metrics": [
                {"name": metric.name, "value": metric.value}
                for metric in llm_summary.key_metrics
            ],
        }

        logging.info("process_week completed successfully!")

        # Print output for debugging
        print("Output to Q2:", json.dumps(output, indent=4))  # Pretty print JSON output
        return output  # Return JSON-serializable dictionary

    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        raise
    except Exception as e:
        logging.error(f"Error in process_week: {e}")
        raise


def save_summary_to_database(start_date: str, llm_summary: SummaryOutput):
    """
    Saves the structured summary result and its key metrics to the database.

    Args:
        start_date (str): Start date for the summary (YYYY-MM-DD).
        llm_summary (SummaryOutput): The structured summary result.
    """
    try:
        # Pre-save validation: Ensure LLM summary contains necessary data
        if not llm_summary.dataset_summary:
            raise ValidationError("Dataset summary is missing in the LLM output.")
        if not llm_summary.key_metrics:
            raise ValidationError("Key metrics are missing in the LLM output.")

        with transaction.atomic():
            logging.info(
                f"Saving summary for start_date={start_date} to the database..."
            )

            # Create the Summary object
            summary = Summary.objects.create(
                start_date=start_date,
                dataset_summary=llm_summary.dataset_summary,
            )

            # Create KeyMetric objects one by one (could also be batched if needed)
            for metric in llm_summary.key_metrics:
                KeyMetric.objects.create(
                    summary=summary,
                    name=metric.name,
                    value=metric.value,
                )

            # Log successful save with details
            logging.info(
                f"Saved summary for start_date={start_date} with {len(llm_summary.key_metrics)} key metrics."
            )
            return summary  # Optional: Return the created Summary object

    except ValidationError as ve:
        logging.error(f"Validation error while saving summary: {ve}")
        raise
    except IntegrityError as ie:
        logging.error(f"Database integrity error: {ie}")
        raise ValidationError(
            "A database integrity error occurred while saving."
        ) from ie
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise RuntimeError("Failed to save summary and key metrics.") from e


# def save_summary_to_file(start_date: str, llm_summary: SummaryOutput):
#     """
#     Saves the structured summary result to a JSON file in the same format as the database.

#     Args:
#         start_date (str): Start date for the summary (YYYY-MM-DD).
#         llm_summary (SummaryOutput): The structured summary result.
#     """
#     try:
#         file_path = f"summary_output_{start_date}.json"
#         logging.info(f"Saving summary result to {file_path}...")
#         data = {
#             "start_date": start_date,
#             "dataset_summary": llm_summary.dataset_summary,
#             "key_metrics": [
#                 {"name": metric.name, "value": metric.value}
#                 for metric in llm_summary.key_metrics
#             ],
#         }
#         with open(file_path, "w") as json_file:
#             json.dump(data, json_file, indent=4)
#         logging.info("Summary result saved successfully.")
#     except Exception as e:
#         logging.error(f"Failed to save summary result to file: {e}")
#         raise
