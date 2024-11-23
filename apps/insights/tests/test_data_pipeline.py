# tests/test_data_pipeline.py
import os
import pytest
from apps.insights.data_pipeline import run_pipeline


def test_run_pipeline():
    """
    Test the data pipeline with the actual CSV file and a fixed start date.
    Prints the output for manual verification.
    """
    file_path = "../data/ga4_data.csv"  # Relative path to your actual data file
    start_date = "2024-01-01"  # Example start date

    try:
        # Run the pipeline
        run_pipeline(file_path, start_date)
        print("Pipeline ran successfully.")
    except Exception as e:
        pytest.fail(f"Pipeline failed: {e}")
