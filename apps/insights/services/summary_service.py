# app/insights/services/summary_service.py
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

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# FIXME! process_summary()
def process_week(start_date: str, week_number: int) -> dict:
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

        # Adjust start_date for previous week
        start_date_dt = pd.to_datetime(start_date)
        if week_number == 2:
            logging.info("Adjusting start_date for previous week.")
            start_date_dt -= pd.Timedelta(days=7)

        # FIXME! DEBUGGING
        print("DEBUG! Start_date:", start_date_dt)

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
        week_df = processor.filter(start_date_dt.strftime("%Y-%m-%d"), week_number)
        logging.info(f"Filtering complete! Filtered rows: {len(week_df)}")

        # Step 5: Generate statistical overview
        logging.info("Generating statistical overview...")
        processor.generate_overview(week_df, f"Week {week_number}")

        # Step 6: Generate LLM summary
        logging.info("Calling LLM to generate summary...")
        statistical_summary = week_df.describe().to_string()
        llm_summary = generate_summary(statistical_summary)
        logging.info("LLM summary generated successfully!")

        # Step 7: Save results to database
        logging.info("Saving results to database...")
        save_summary_to_database(
            start_date_dt.strftime("%Y-%m-%d"),
            llm_summary,
        )

        # FIXME! Remove serializer?
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
        with transaction.atomic():
            logging.info(f"Saving summary for {start_date} to the database...")
            summary = Summary.objects.create(
                start_date=start_date,
                dataset_summary=llm_summary.dataset_summary,
            )
            for metric in llm_summary.key_metrics:
                KeyMetric.objects.create(
                    summary=summary,
                    name=metric.name,
                    value=metric.value,
                )
            logging.info("Summary and key metrics saved successfully.")
    except Exception as e:
        logging.error(f"Failed to save summary and key metrics to the database: {e}")
        raise


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
