import os
import logging
import redis

from settings import DEBUG, LOCAL

# Indicates whether the environment is simulated (e.g., local development)
SIMULATED_ENV = LOCAL

logger = logging.getLogger("redis_db")

# Define a default Redis URL for local and Docker environments
DEFAULT_REDIS_URL = "redis://redis:6379/5"

# Setup Redis connection
try:
    if LOCAL:
        from settings.local import REDIS_URL

        # Use REDIS_URL from settings.local or fallback to Docker Redis service
        redis_db = redis.from_url(REDIS_URL or DEFAULT_REDIS_URL)
    else:
        # Use REDIS_URL from environment variable or fallback to Docker Redis service
        redis_db = redis.from_url(os.environ.get("REDIS_URL", DEFAULT_REDIS_URL))

    # Log Redis connection details
    if DEBUG:
        logger.info("Redis connection established for app database.")
        redis_info = redis_db.info()
        used_memory, maxmemory = redis_info.get("used_memory"), redis_info.get(
            "maxmemory", 0
        )
        maxmemory_human = redis_info.get("maxmemory_human", "N/A")
        if maxmemory > 0:
            usage_percent = round(100 * used_memory / maxmemory, 2)
            logger.info(
                f"Redis currently consumes {usage_percent}% out of {maxmemory_human}"
            )

except redis.ConnectionError as e:
    # Log critical error if Redis connection fails
    logger.critical("Redis connection failed! Ensure Redis is running and accessible.")
    raise e
