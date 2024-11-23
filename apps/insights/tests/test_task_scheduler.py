import os
import pytest
import time
from django_q.tasks import async_task, result
import redis


# Ensure migrations are applied for the test database
@pytest.fixture(autouse=True)
def apply_migrations(db):
    from django.core.management import call_command

    call_command("migrate")


@pytest.mark.django_db
def test_process_week_task():
    """
    Test the process_week_task function via async_task and print the result.
    """
    # Ensure critical environment variables are set
    os.environ.setdefault("DJANGO_SECRET_KEY", "test_secret_key")
    os.environ.setdefault("REDIS_URL", "redis://redis:6379/5")
    os.environ.setdefault("REDIS_HOST", "redis")
    os.environ.setdefault("REDIS_PORT", "6379")
    os.environ.setdefault("REDIS_DB", "5")

    # Debug environment variables
    print("DEBUG: Environment Variables:")
    print(f"REDIS_URL: {os.getenv('REDIS_URL')}")
    print(f"REDIS_HOST: {os.getenv('REDIS_HOST')}")
    print(f"REDIS_PORT: {os.getenv('REDIS_PORT')}")
    print(f"REDIS_DB: {os.getenv('REDIS_DB')}")

    # Ensure the Redis client connects properly
    try:
        redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
        assert redis_client.ping(), "Redis connection failed!"
        print("DEBUG: Redis connection successful.")
    except Exception as redis_error:
        pytest.fail(f"Redis setup failed: {redis_error}")

    # Correctly resolve the file path for the input data
    file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data/ga4_data.csv")
    )
    print(f"DEBUG: Resolved file path for GA4 data: {file_path}")
    start_date = "2024-01-01"  # Example start date
    week_number = 1  # Testing for Week 1

    # Trigger the async task and wait for the result
    try:
        # Trigger the task via Django-Q
        task_id = async_task(
            "apps.insights.tasks.process_week_task",
            file_path,
            start_date,
            week_number,
        )
        print(f"DEBUG: Task {task_id} triggered successfully.")

        # Wait for the result with retries
        retries = 10
        result_data = None
        while retries > 0:
            result_data = result(task_id)
            if result_data is not None:
                break
            retries -= 1
            time.sleep(1)  # Wait 1 second before retrying

        # Validate and print the result
        assert result_data is not None, "Task did not return a result."
        print("DEBUG: Task Result:")
        print(result_data)

    except Exception as task_error:
        pytest.fail(f"Task test failed: {task_error}")
