from django_q.tasks import async_task
import redis

# Initialize Redis connection
r = redis.Redis()


# Summary example
def create_summary(start_date, week_number):
    # Logic to create a summary
    r.set("Summary {week_number}", True)


def comparison_hook(task):
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
