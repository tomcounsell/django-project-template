# apps/insights/get_summaries.py
# This file forms the basis of the Django-Q2 tasks.py class and data pipeline

import os
from .services.csv_reader import load_csv
from .services.data_validator import validate_columns
from .services.data_cleaner import clean_data
from .services.data_filter import filter_data
from .services.data_overview import generate_overview
from .services.openai.llm_integration import generate_summary  # Import new service


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
    print("Generating statistical overviews...")
    week1_summary = week1_df.describe().to_string()
    week2_summary = week2_df.describe().to_string()

    # Step 7: Generate LLM summaries
    print("Generating LLM summaries...")
    week1_llm_summary = generate_summary(week1_summary)
    week2_llm_summary = generate_summary(week2_summary)

    # Step 8: Display LLM results
    print("\nLLM Summary - Week 1:")
    print(week1_llm_summary.plain_english_summary)
    print("\nKey Metrics:")
    for metric in week1_llm_summary.key_metrics:
        print(f"{metric.metric_name}: {metric.value}")

    print("\nLLM Summary - Week 2:")
    print(week2_llm_summary.plain_english_summary)
    print("\nKey Metrics:")
    for metric in week2_llm_summary.key_metrics:
        print(f"{metric.metric_name}: {metric.value}")


if __name__ == "__main__":
    main()
