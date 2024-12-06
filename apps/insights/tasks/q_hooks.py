from django_q.tasks import async_task
import redis

# Initialize Redis connection
r = redis.Redis()

# Method utilizing Redis keys to schedule and check parallel asynchronous tasks


def comparison_hook(task: dict):
    if r.get("Summary 1") and r.get("Summary 2"):
        async_task("apps.insights.tasks.comparison_task")
        r.delete("Summary 1")
        r.delete("Summary 2")


# Schedule parallel asynchronous tasks with hooks
async_task(
    "apps.insights.services.summary_service.create_summary",
    start_date,
    1,
    hook=comparison_hook,
)
async_task(
    "apps.insights.services.summary_service.create_summary",
    start_date,
    2,
    hook=comparison_hook,
)
