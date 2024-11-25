# apps/insights/services/comparison_pipeline.py
from apps.insights.services.comparison_service import (
    process_comparison,
    save_comparison_to_database,
)
from apps.insights.models.summary import Summary
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# FIXME! def request_summary(start_date)
# FIXME! def request_comparison(start_date)


def run_comparison_task(start_date: str):
    """
    Fetch summaries for current week and past week from the database,
    pass them to the comparison service, and save the results to the database.
    """
    try:
        logger.info("Fetching summaries from the database...")
        start_date_week1 = datetime.strptime(start_date, "%Y-%m-%d")
        start_date_week2 = start_date_week1 - timedelta(days=7)

        # Fetch summaries
        summary1 = Summary.objects.get(start_date=start_date_week1.strftime("%Y-%m-%d"))
        summary2 = Summary.objects.get(start_date=start_date_week2.strftime("%Y-%m-%d"))

        logger.info(f"Current Week Summary ID: {summary1.id}")
        logger.info(f"Past Week Summary ID: {summary2.id}")

        # Run the comparison service
        logger.info("Running comparison service...")
        data_summary1 = {
            "dataset_summary": summary1.dataset_summary,
            "key_metrics": [
                {"name": metric.name, "value": metric.value}
                for metric in summary1.key_metrics.all()
            ],
        }
        data_summary2 = {
            "dataset_summary": summary2.dataset_summary,
            "key_metrics": [
                {"name": metric.name, "value": metric.value}
                for metric in summary2.key_metrics.all()
            ],
        }

        comparison_result = process_comparison(data_summary1, data_summary2)

        # Log the comparison result
        logger.info("Comparison Service Output:")
        logger.info(f"Comparison Summary: {comparison_result.comparison_summary}")
        for metric in comparison_result.key_metrics_comparison:
            logger.info(
                f"{metric.name}: Current Week = {metric.value1}, Past Week = {metric.value2} ({metric.description})"
            )

        # Save the comparison result to the database
        logger.info("Saving comparison result to the database...")
        save_comparison_to_database(summary1.id, summary2.id, comparison_result)
        logger.info("Comparison result has been saved successfully!")

    except Summary.DoesNotExist as e:
        logger.error(f"Summary not found: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")


# Run the comparison service
# comparison_result = process_comparison(data_summary1, data_summary2)

# # Save the comparison result to the database
# # You need to replace summary1_id and summary2_id with actual IDs from your database
# summary1_id = 11  # Replace with actual Week 1 Summary ID
# summary2_id = 12  # Replace with actual Week 2 Summary ID
# save_comparison_to_database(summary1_id, summary2_id, comparison_result)

# print("Comparison result has been saved to the database successfully!")
