# apps/insights/services/openai/comparison_generator.py

import logging
import functools
import inspect
from pydantic import BaseModel, ValidationError
import redis
from django.conf import settings
from instructor import from_openai
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)
from .schemas import ComparisonOutput
from .prompts.comparison import COMPARISON_PROMPT  # Import the comparison prompt
from .logging import (
    log_completion_kwargs,
    log_completion_response,
    log_completion_error,
    log_parse_error,
)

# Load OpenAI API key from settings
openai_api_key = settings.OPENAI_API_KEY

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY must be set in environment variables.")

# Initialize OpenAI client
client = from_openai(OpenAI(api_key=openai_api_key))

# Register Instructor hooks for logging
client.on("completion:kwargs", log_completion_kwargs)
client.on("completion:response", log_completion_response)
client.on("completion:error", log_completion_error)
client.on("parse:error", log_parse_error)

# Initialize Redis client for caching
cache = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
)


def instructor_cache(func):
    """
    Caches a function that returns a Pydantic model.
    """
    return_type = inspect.signature(func).return_annotation
    if not issubclass(return_type, BaseModel):
        raise ValueError("Return type must be a Pydantic model.")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a stable, hashable representation of arguments
        key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
        # Check if the result is already cached
        if (cached := cache.get(key)) is not None:
            try:
                # Deserialize the cached data
                return return_type.model_validate_json(cached)
            except ValidationError as e:
                logging.warning(
                    "Cache deserialization error: %s. Recomputing result.", e
                )

        # Compute the result if not cached
        result = func(*args, **kwargs)

        # Serialize and store the result in Redis with a TTL
        cache.set(key, result.model_dump_json(), ex=3600)
        return result

    return wrapper


# Retry logic for transient errors
@retry(
    stop=stop_after_attempt(settings.OPENAI_RETRY_ATTEMPTS),
    wait=wait_exponential(
        multiplier=settings.OPENAI_RETRY_WAIT_MULTIPLIER,
        min=settings.OPENAI_RETRY_WAIT_MIN,
        max=settings.OPENAI_RETRY_WAIT_MAX,
    ),
)
@instructor_cache
def call_openai_api(prompt: str) -> ComparisonOutput:
    """
    Makes a call to the OpenAI API with a retry mechanism for transient errors.

    Args:
        prompt (str): The input prompt for the OpenAI model.

    Returns:
        ComparisonOutput: A structured comparison containing a summary and key metrics comparison.
    """
    try:
        # Make the API call
        return client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            response_model=ComparisonOutput,
        )
    except Exception as e:
        logging.error(f"Error during OpenAI API call: {e}")
        raise


def generate_comparison(summary1: str, summary2: str) -> ComparisonOutput:
    """
    Generates a structured comparison between two dataset summaries using the OpenAI API.

    Args:
        summary1 (str): The first dataset summary as a string (Current Week).
        summary2 (str): The second dataset summary as a string (Past Week).

    Returns:
        ComparisonOutput: A structured comparison containing a summary and key metrics comparison.
    """
    # Format the prompt using COMPARISON_PROMPT
    prompt = COMPARISON_PROMPT.format(summary1=summary1, summary2=summary2)

    try:
        logging.info("Requesting dataset comparison from OpenAI...")

        # Retry-enabled API call
        response = call_openai_api(prompt)

        # Log successful response
        logging.info("Successfully received structured response.")
        return response

    except Exception as e:
        logging.error(f"Error generating comparison: {e}")
        raise ValueError("Failed to generate comparison using OpenAI.") from e
