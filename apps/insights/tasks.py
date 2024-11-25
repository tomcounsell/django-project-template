# apps/insights/tasks.py

from django_q.tasks import schedule
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def schedule_summary_tasks(start_date):
    """
    Schedule tasks to process summaries for Week 1 and Week 2.
    """
    # Convert start_date to timezone-aware datetime
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if timezone.is_naive(start_date):
        start_date = timezone.make_aware(start_date, timezone.get_current_timezone())

    # Wait 1 minute before scheduling the first task
    group_id = f"summary-{start_date.isoformat()}"
    next_run_time = timezone.now() + timedelta(seconds=5)

    # Schedule Task 1: Week 1 Summary
    task_1_id = schedule(
        "apps.insights.services.summary_service.process_week",
        start_date.strftime("%Y-%m-%d"),
        1,
        name=f"Week 1 Summary Task - {start_date.date()}",
        schedule_type="O",
        next_run=next_run_time,
        q_options={"group": group_id},
    )
    logger.info(f"Scheduled Task 1 for Week 1 with ID {task_1_id}")

    # Schedule Task 2: Week 2 Summary
    task_2_id = schedule(
        "apps.insights.services.summary_service.process_week",
        start_date.strftime("%Y-%m-%d"),
        2,
        name=f"Week 2 Summary Task - {start_date.date()}",
        schedule_type="O",
        next_run=next_run_time + timedelta(seconds=5),  # Starts 5 seconds after Task 1
        q_options={"group": group_id},
    )
    logger.info(f"Scheduled Task 2 for Week 2 with ID {task_2_id}")
