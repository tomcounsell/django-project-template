# apps/insights/tasks.py
from django_q.tasks import schedule, async_task
from django.utils.timezone import now, timedelta
import logging

logger = logging.getLogger(__name__)


def schedule_summary_tasks(start_date):
    """
    Schedule tasks to process summaries for Week 1 and Week 2 with proper sequencing.
    """
    group_id = f"summary-{start_date}"  # Group ID for tracking
    next_run_time = now() + timedelta(seconds=5)  # 5 seconds from now

    # Schedule Task 1: Process Week 1
    task_1_id = schedule(
        "apps.insights.services.summary_service.process_week",
        start_date,
        1,
        name=f"Process Week 1 - {start_date}",
        schedule_type="O",  # One-off execution
        next_run=next_run_time,
        group=group_id,
        hook="apps.insights.tasks.trigger_week_2_task",  # Hook to trigger Task 2
    )

    logger.info(f"Task 1 for Week 1 scheduled with ID {task_1_id} in group {group_id}.")


def trigger_week_2_task(task):
    """
    Trigger Task 2 (Week 2) after Task 1 completes successfully.
    """
    if task.get("success"):
        start_date, week_number = task["args"]
        if week_number == 1:  # Ensure it's Week 1 before triggering Week 2
            async_task(
                "apps.insights.services.summary_service.process_week",
                start_date,
                2,
                group=f"summary-{start_date}",
                name=f"Process Week 2 - {start_date}",
            )
            logger.info(f"Task 2 for Week 2 triggered for start_date {start_date}.")


#  After the two grouped tasks, the Step 3 task (comparison task) accepts these returned summaries as inputs from summary_services.
