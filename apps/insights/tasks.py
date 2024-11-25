from apps.insights.services.summary_service import process_week
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_summary_task():
    """
    Task to run the summary service with start date and week number.
    """
    try:
        start_date = "2024-01-15"  # Hardcoded start date
        week_number = 1  # Always process week 1 for this task

        logging.info(
            f"Running summary task for start_date={start_date}, week_number={week_number}"
        )
        process_week(start_date=start_date, week_number=week_number)

        logging.info("Summary task completed successfully.")
    except Exception as e:
        logging.error(f"Error in summary task: {e}")
        raise
