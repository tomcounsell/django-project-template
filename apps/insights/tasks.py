# apps/insights/tasks.py
"""
Chaining Tasks:
- One Function Call: Trigger all tasks with a single function.
- Sequential Execution: Tasks run one after another in the correct order.
- Simplicity: Minimal code complexity, all in one file.
- Integration: Easy to tie into a button click or any other trigger.
"""

from datetime import datetime, date, timedelta
from django.conf import settings
from django.utils.timezone import now  # Correct import for timezone.now
from django_q.tasks import schedule, Chain
import logging

logger = logging.getLogger(__name__)


def schedule_summary_chain(start_date):
    """
    Wrapper function to schedule the summary chain after a delay.

    Schedules the `schedule_summary_tasks` function to run
    after a predefined delay with `start_date`.
    """
    time_delay = getattr(settings, "SUMMARY_TASK_TIME_DELAY", 60)

    logger.info(
        "Preparing to schedule summary tasks with a delay of %d seconds...", time_delay
    )

    # Convert start_date to string
    start_date_str = (
        start_date.strftime("%Y-%m-%d")
        if isinstance(start_date, (datetime, date))
        else str(start_date)
    )

    try:
        schedule(
            "apps.insights.tasks.schedule_summary_tasks",  # Function path
            start_date_str,  # Positional argument as string
            name="summary_task_chain",  # Task name for identification
            schedule_type="O",  # 'O' stands for Once
            next_run=now()
            + timedelta(
                seconds=time_delay
            ),  # Schedule to run after `time_delay` seconds
        )
        logger.info(
            "Scheduled `schedule_summary_tasks` to run in %d seconds with start_date: %s.",
            time_delay,
            start_date_str,
        )
    except Exception as e:
        logger.error("Failed to schedule the summary tasks: %s", e)
        raise


def schedule_summary_tasks(start_date):
    """
    Run tasks to process summaries for Week 1, Week 2, and Comparison.
    """
    # Convert start_date to string # FIXME Remove repeated type conversion
    start_date_str = (
        start_date.strftime("%Y-%m-%d")
        if isinstance(start_date, (datetime, date))
        else str(start_date)
    )

    # Create a task chain
    chain = Chain()

    # Append Task 1: Generate current week summary
    chain.append(
        "apps.insights.services.summary_service.process_week",
        start_date_str,
        1,
        q_options={"task_name": "Generate_Current_Week_Summary"},
    )
    logger.info("Added Task 1 to chain: Generate Current Week Summary.")

    # Append Task 2: Generate past week summary
    chain.append(
        "apps.insights.services.summary_service.process_week",
        start_date_str,
        2,
        q_options={"task_name": "Generate_Previous_Week_Summary"},
    )
    logger.info("Added Task 2 to chain: Generate Past Week Summary.")

    # Append Task 3: Generate comparison of current and past weeks summaries
    chain.append(
        "apps.insights.services.comparison_service.create_comparison",
        start_date_str,
        q_options={"task_name": "Generate_Comparison"},
    )
    logger.info("Added Task 3 to chain: Generate comparison.")

    # Run the task chain
    chain.run()
    logger.info(f"Ran summary chain for start date {start_date_str}.")
