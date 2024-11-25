from apps.insights.models.summary import Summary
from apps.insights.services.comparison_service import process_comparison
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def run_comparison_task(start_date: str) -> dict:
    """
    Fetch summaries for Week 1 and Week 2 from the database, then pass them to the comparison service.

    Args:
        start_date (str): Start date for Week 1 in the format 'YYYY-MM-DD'.

    Returns:
        dict: The result of the comparison service.
    """
    try:
        logger.info(f"Starting comparison task for start_date: {start_date}")

        # Convert start_date to datetime
        start_date_week1 = datetime.strptime(start_date, "%Y-%m-%d")
        logger.info(f"Week 1 Start Date: {start_date_week1}")
        start_date_week2 = start_date_week1 + timedelta(days=7)
        logger.info(f"Week 2 Start Date: {start_date_week2}")

        # Fetch summaries
        logger.info("Fetching summaries from the database...")
        summary1 = Summary.objects.get(start_date=start_date_week1.strftime("%Y-%m-%d"))
        logger.info(f"Fetched Week 1 Summary: {summary1}")
        summary2 = Summary.objects.get(start_date=start_date_week2.strftime("%Y-%m-%d"))
        logger.info(f"Fetched Week 2 Summary: {summary2}")

        # Prepare structured data for comparison_service
        data_summary1 = {
            "dataset_summary": summary1.dataset_summary,
            "key_metrics": [
                {"name": metric.name, "value": metric.value}
                for metric in summary1.key_metrics.all()
            ],
        }
        logger.info(f"Prepared Data Summary 1: {data_summary1}")

        data_summary2 = {
            "dataset_summary": summary2.dataset_summary,
            "key_metrics": [
                {"name": metric.name, "value": metric.value}
                for metric in summary2.key_metrics.all()
            ],
        }
        logger.info(f"Prepared Data Summary 2: {data_summary2}")

        # Pass summaries to the comparison_service
        logger.info("Passing summaries to comparison_service...")
        comparison_result = process_comparison(data_summary1, data_summary2)

        logger.info("Comparison completed successfully!")
        return comparison_result

    except Summary.DoesNotExist as e:
        logger.error(f"Summary not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while running comparison task: {e}")
        raise
