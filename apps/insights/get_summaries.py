# apps/insights/get_summaries.py
# This file forms the basis of the Django-Q2 tasks.py class and data pipeline

import os
from .services.csv_processor import CSVProcessor
from .services.openai.llm_integration import generate_summary  # Import updated service


def main():
    # Resolve the file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "./data/ga4_data.csv")

    # Initialize the CSVProcessor
    processor = CSVProcessor(file_path)

    # Define the start date for filtering
    start_date = "2024-01-01"  # FIXME: Make this dynamic later

    # Run the CSV processing pipeline
    week1_df, week2_df = processor.process(start_date)

    # Step 7: Generate statistical summaries
    print("Generating statistical summaries...")
    week1_summary = week1_df.describe().to_string()
    week2_summary = week2_df.describe().to_string()

    # Step 8: Generate LLM summaries
    print("Generating LLM summaries...")
    week1_llm_summary = generate_summary(week1_summary)
    week2_llm_summary = generate_summary(week2_summary)

    # Step 9: Display LLM results
    print("\nLLM Summary - Week 1:")
    print(week1_llm_summary.dataset_summary)  # Updated field name
    print("\nKey Metrics:")
    for metric in week1_llm_summary.key_metrics:
        print(f"{metric.name}: {metric.value}")  # Updated field names

    print("\nLLM Summary - Week 2:")
    print(week2_llm_summary.dataset_summary)  # Updated field name
    print("\nKey Metrics:")
    for metric in week2_llm_summary.key_metrics:
        print(f"{metric.name}: {metric.value}")  # Updated field names


if __name__ == "__main__":
    main()
