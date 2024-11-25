# apps/insights/tasks.py
"""
- One Function Call: Trigger all tasks with a single function.
- Sequential Execution: Tasks run one after another in the correct order.
- Simplicity: Minimal code complexity, all in one file.
- Integration: Easy to tie into a button click or any other trigger in your application.

"""
from django_q.tasks import Chain
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def schedule_summary_tasks(start_date):
    """
    Run tasks to process summaries for Week 1, Week 2, and Comparison.
    """
    # Convert start_date to string
    if isinstance(start_date, datetime):
        start_date_str = start_date.strftime("%Y-%m-%d")
    else:
        start_date_str = start_date

    # Create a task chain
    chain = Chain()

    # Append Task 1: Generate Week 1 summary
    chain.append(
        "apps.insights.services.summary_service.process_week",
        start_date_str,
        1,
        q_options={"task_name": "Generate_Current_Week_Summary"},
    )
    logger.info("Added Task 1 to chain: Generate Current Week Summary.")

    # Append Task 2: Generate Week 2 summary
    chain.append(
        "apps.insights.services.summary_service.process_week",
        start_date_str,
        2,
        q_options={"task_name": "Generate_Past_Week_Summary"},
    )
    logger.info("Added Task 2 to chain: Generate Past Week Summary.")

    # Append Task 3: Generate comparison of Weeks 1 and 2
    chain.append(
        "apps.insights.services.comparison_pipeline.run_comparison_task",
        start_date_str,
        q_options={"task_name": "Generate_Comparison"},
    )
    logger.info("Added Task 3 to chain: Run comparison.")

    # Run the task chain
    chain.run()
    logger.info(f"Ran summary chain for start date {start_date_str}.")