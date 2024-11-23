# apps/insights/services/data_pipeline.py
import logging
import os
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
        processor.process(start_date)

        logging.info("Generating summaries with OpenAI...")

        # Statistical summaries from CSVProcessor
        week1_summary = processor.df.describe().to_string()
        week2_summary = (
            processor.df.describe().to_string()
        )  # Replace with Week 2 if separate DataFrame is used

        # Generate summaries using OpenAI
        week1_llm_summary = generate_summary(week1_summary)
        week2_llm_summary = generate_summary(week2_summary)

        # Log and display LLM results
        logging.info("\nLLM Summary - Week 1:")
        print(week1_llm_summary.dataset_summary)
        logging.info("Key Metrics:")
        for metric in week1_llm_summary.key_metrics:
            print(f"{metric.name}: {metric.value} ({metric.description})")

        logging.info("\nLLM Summary - Week 2:")
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
