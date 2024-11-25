# apps/insights/tasks.py

from django_q.tasks import schedule
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def schedule_single_summary_task(start_date):
    """
    Schedule a single task to process summaries for Week 1.
    """
    # Ensure start_date is in the correct format
    if isinstance(start_date, str):
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError as e:
            logger.error(
                f"Invalid start_date format: {start_date}. Expected YYYY-MM-DD."
            )
            raise e

    # Ensure start_date is timezone-aware
    if timezone.is_naive(start_date):
        start_date = timezone.make_aware(start_date, timezone.get_current_timezone())

    next_run_time = timezone.now() + timezone.timedelta(seconds=5)  # 5 seconds delay

    # Schedule the task
    task_id = schedule(
        "apps.insights.services.summary_service.process_week",
        start_date.strftime("%Y-%m-%d"),  # Pass the start_date as a string again
        1,  # Week 1
        name=f"Process Week 1 - {start_date.date()}",
        schedule_type="O",  # One-off execution
        next_run=next_run_time,
    )

    logger.info(f"Task scheduled with ID {task_id} for Week 1 - {start_date.date()}.")


# def trigger_week_2_task(task):
#     """
#     Trigger Task 2 (Week 2) after Task 1 completes successfully.
#     """
#     if task.success:
#         start_date, week_number = task.args

#         # Ensure that start_date is timezone-aware
#         if timezone.is_naive(start_date):
#             start_date = timezone.make_aware(
#                 start_date, timezone.get_current_timezone()
#             )

#         if week_number == 1:  # Ensure it's Week 1 before triggering Week 2
#             async_task(
#                 "apps.insights.services.summary_service.process_week",
#                 start_date,
#                 2,
#                 group=f"summary-{start_date.isoformat()}",
#                 name=f"Process Week 2 - {start_date.date()}",
#             )
#             logger.info(
#                 f"Task 2 for Week 2 triggered by Task ID {task.id} for start_date {start_date}."
#             )
#     else:
#         logger.error(f"Task 1 failed for start_date {start_date}. Error: {task.result}")

#  After the two grouped tasks, the Step 3 task (comparison task) accepts these returned summaries as inputs from summary_services.
