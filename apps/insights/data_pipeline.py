# apps/insights/data_pipeline.py
"""
Title: Data Pipeline for CSV Processing and LLM Integration
Description:
This script orchestrates the data pipeline for processing GA4 CSV data.
It validates, cleans, filters, and generates statistical overviews,
and optionally integrates with an LLM for dataset summaries.

Usage:
Run this file directly to execute the pipeline:
    python -m apps.insights.data_pipeline
"""

import logging
import os
import pandas as pd
from apps.insights.services.csv_processor import CSVProcessor
from apps.insights.services.openai.summary_generator import generate_summary

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_pipeline(file_path: str, start_date: str):
    """
    Orchestrates the CSV processing pipeline and outputs results.
    Args:
        file_path (str): Path to the CSV file.
        start_date (str): Starting date for data filtering (YYYY-MM-DD).
    """
    try:
        logging.info("Initializing CSVProcessor...")
        processor = CSVProcessor(file_path)

        logging.info("Starting the CSV processing pipeline...")
        # Process the file: load, validate, clean, and filter data
        processor.load()
        processor.validate()
        processor.clean()
        week1_df, week2_df = processor.filter(start_date)

        # Calculate week date ranges
        start_date_dt = pd.to_datetime(start_date)
        week1_start = start_date_dt
        week1_end = week1_start + pd.Timedelta(days=6)
        week2_start = week1_end + pd.Timedelta(days=1)
        week2_end = week2_start + pd.Timedelta(days=6)

        # Generate statistical overviews
        logging.info("Generating statistical overviews...")
        logging.info(
            f"\nStatistical Overview - Week 1 (Start: {week1_start.date()}, End: {week1_end.date()}):"
        )
        print(week1_df.describe().to_string())

        logging.info(
            f"\nStatistical Overview - Week 2 (Start: {week2_start.date()}, End: {week2_end.date()}):"
        )
        print(week2_df.describe().to_string())

        # LLM Integration
        logging.info("Generating summaries with OpenAI...")

        week1_summary = week1_df.describe().to_string()
        week2_summary = week2_df.describe().to_string()

        week1_llm_summary = generate_summary(week1_summary)
        week2_llm_summary = generate_summary(week2_summary)

        logging.info(
            f"\nLLM Summary - Week 1 ({week1_start.date()} to {week1_end.date()}):"
        )
        print(week1_llm_summary.dataset_summary)
        logging.info("Key Metrics:")
        for metric in week1_llm_summary.key_metrics:
            print(f"{metric.name}: {metric.value} ({metric.description})")

        logging.info(
            f"\nLLM Summary - Week 2 ({week2_start.date()} to {week2_end.date()}):"
        )
        print(week2_llm_summary.dataset_summary)
        logging.info("Key Metrics:")
        for metric in week2_llm_summary.key_metrics:
            print(f"{metric.name}: {metric.value} ({metric.description})")

        logging.info("Pipeline executed successfully!")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    # Dynamically resolve the path to the CSV file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(
        current_dir, "data/ga4_data.csv"
    )  # Path inside insights
    start_date = "2024-01-01"  # Set your start date
    run_pipeline(csv_file_path, start_date)
