# apps/insights/get_summaries.py
# This file is the basis for the Django-Q2 tasks.py class and data pipeline

import os
from .services.csv_reader import load_csv
from .services.data_validator import validate_columns
from .services.data_cleaner import clean_data
from .services.data_filter import filter_data
from .services.data_overview import generate_overview


def main():
    # Resolve the file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "./data/ga4_data.csv")

    # Step 1: Load the CSV file
    print("Loading CSV...")
    df = load_csv(file_path)

    # Step 2: Validate all columns
    print("Validating columns...")
    validate_columns(df)

    # Step 3: Clean the data
    print("Cleaning data...")
    df = clean_data(df)

    # Step 4: Filter the data into two periods
    print("Filtering data...")
    start_date = "2024-01-01"  # FIXME: Variable input
    week1_df, week2_df = filter_data(df, start_date)

    # Step 5: Output the filtered data
    print("\nFiltered Data - Week 1:")
    print(week1_df)
    print("\nFiltered Data - Week 2:")
    print(week2_df)

    # Step 6: Generate statistical overviews
    generate_overview(week1_df, "Week 1")
    generate_overview(week2_df, "Week 2")


if __name__ == "__main__":
    main()
