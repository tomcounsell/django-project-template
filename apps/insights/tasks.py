# apps/insights/tasks.py

from django_q.tasks import schedule, async_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def schedule_summary_tasks(start_date):
    """
    Schedule tasks to process summaries for Week 1, Week 2, and Comparison.
    """
    # Convert start_date to timezone-aware datetime for Q2 scheduling
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if timezone.is_naive(start_date):
        start_date = timezone.make_aware(start_date, timezone.get_current_timezone())

    # Define group ID for tasks
    group_id = f"summary-{start_date.isoformat()}"
    next_run_time = timezone.now() + timedelta(seconds=5)

    # Schedule Task 1: Generate Week 1 summary
    schedule(
        "apps.insights.services.summary_service.process_week",
        start_date.strftime("%Y-%m-%d"),
        1,
        name=f"Week 1 Summary Task - {start_date.date()}",
        schedule_type="O",
        next_run=next_run_time,
        q_options={"group": group_id},
    )
    logger.info("Scheduled Task 1 to generate Week 1 summary.")

    # Schedule Task 2: Generate Week 2 summary
    schedule(
        "apps.insights.services.summary_service.process_week",
        start_date.strftime("%Y-%m-%d"),
        2,
        name=f"Week 2 Summary Task - {start_date.date()}",
        schedule_type="O",
        next_run=next_run_time + timedelta(seconds=5),  # Delay 5 seconds
        q_options={"group": group_id},
    )
    logger.info("Scheduled Task 2 to generate Week 2 summary.")

    # Async Task 3: Generate comparison #! FIXME Remove indefinite wait
    async_task(  # Waits for Tasks 1 and 2 to complete
        "apps.insights.services.comparison_pipeline.run_comparison_task",
        start_date.strftime("%Y-%m-%d"),
        group=group_id,
        name=f"Comparison Task - {start_date}",
    )
    logger.info("Scheduled Task 3 to run after Tasks 1 and 2 complete.")
