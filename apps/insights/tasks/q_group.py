import logging
import time
from django_q.tasks import async_task, result_group

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# Wait for group tasks to complete
def await_group_completion(group_id: str):
    logger.info(f"Waiting for task group '{group_id}' to complete...")
    while not result_group(group_id, count=2):  # Wait for both tasks in the group
        logger.debug(f"Group '{group_id}' still running...")
        time.sleep(1)  # Poll every second
    logger.info(f"All tasks in group '{group_id}' have completed.")
    return "Group tasks completed."


# Schedule the tasks
def schedule_tasks(start_date: str):
    group_id = "summary_tasks"  # Group identifier for concurrent tasks
    logger.info(
        f"Scheduling tasks for group '{group_id}' with start_date '{start_date}'."
    )

    # Schedule the two concurrent summary tasks
    async_task(
        "apps.insights.services.summary_service.create_summary",
        start_date,
        1,
        group=group_id,
    )
    logger.debug(f"Task 1 (create_summary) added to group '{group_id}'.")

    async_task(
        "apps.insights.services.summary_service.create_summary",
        start_date,
        2,
        group=group_id,
    )
    logger.debug(f"Task 2 (create_summary) added to group '{group_id}'.")

    # Wait for group completion
    await_group_task_id = async_task(
        "apps.insights.tasks_group.await_group_completion", group_id
    )
    logger.info(f"Await group completion task queued (Task ID: {await_group_task_id}).")

    # Schedule the comparison task only after the await_group_completion task finishes
    comparison_task_id = async_task(
        "apps.insights.services.comparison_service.create_comparison",
        start_date,
        hook=await_group_task_id,  # Enforce the dependency
    )
    logger.info(
        f"Comparison task queued with dependency on group completion (Task ID: {comparison_task_id})."
    )
