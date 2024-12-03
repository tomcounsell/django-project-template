from django_q.tasks import async_task, result_group
import time
from datetime import datetime


# Wait for the group tasks to complete by querying the result_group
def await_group_completion(group_id: str):
    print(f"Waiting for task group '{group_id}' to complete...")
    while not result_group(group_id, count=2):  # Wait for both tasks in the group
        time.sleep(1)  # Poll every second
    print(f"All tasks in group '{group_id}' have completed.")
    return "Group tasks completed."


# Schedule the tasks
def schedule_tasks(start_date: str):
    group_id = "summary_tasks"  # Group identifier for concurrent tasks

    # Schedule the two parallel summary tasks
    async_task(
        "apps.insights.services.summary_service.create_summary",
        start_date,
        1,
        group=group_id,
    )
    async_task(
        "apps.insights.services.summary_service.create_summary",
        start_date,
        2,
        group=group_id,
    )

    # Wait for group completion, then schedule the comparison task
    async_task("apps.insights.tasks_group.wait_for_group_completion", group_id)
    async_task(
        "apps.insights.services.comparison_service.create_comparison", start_date
    )
