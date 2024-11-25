from datetime import datetime, timedelta
from django_q.tasks import async_task, schedule
from apps.insights.services.summary_service import process_week
import logging

logger = logging.getLogger(__name__)


def schedule_summary_tasks(start_date):
    """
    Schedule tasks to process summaries for Week 1 and Week 2 sequentially.
    """
    group_id = f"summary-{start_date}"  # Group ID for tracking

    # Calculate 5 seconds from now for the first task
    next_run_time = datetime.now() + timedelta(seconds=5)

    # Chain the tasks: Task 1 (Week 1) triggers Task 2 (Week 2)
    schedule(
        "django_q.tasks.chain",
        [
            ["apps.insights.services.summary_service.process_week", start_date, 1],
            ["apps.insights.services.summary_service.process_week", start_date, 2],
        ],
        schedule_type="O",  # Single execution
        next_run=next_run_time,  # Scheduled 5 seconds from now
        group=group_id,
    )

    logger.info(f"Week 1 and 2 tasks now processing {group_id}.")


#  After the two grouped tasks, the Step 3 task (comparison task) accepts these returned summaries as inputs from summary_services.
