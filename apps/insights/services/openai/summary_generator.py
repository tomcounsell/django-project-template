# apps/insights/services/openai/summary_generator.py

import logging
import functools
import inspect
from pydantic import BaseModel, ValidationError
import redis
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)
from django.conf import settings
from instructor import from_openai
from openai import OpenAI
from .schemas import SummaryOutput
from .prompts.summary import SUMMARY_PROMPT_TEMPLATE


# Load OpenAI API key from settings
openai_api_key = settings.OPENAI_API_KEY

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY must be set in environment variables.")

# Initialize OpenAI client
client = from_openai(OpenAI(api_key=openai_api_key))

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
def call_openai_api(prompt: str) -> SummaryOutput:
    """
    Makes a call to the OpenAI API with a retry mechanism for transient errors.

    Args:
        prompt (str): The input prompt for the OpenAI model.

    Returns:
        SummaryOutput: A structured summary containing dataset insights and key metrics.
    """
    try:
        # Make the API call
        return client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            response_model=SummaryOutput,
        )
    except Exception as e:
        logging.error("Error during OpenAI API call: %s", e)
        raise


def generate_summary(statistical_summary: str) -> SummaryOutput:
    """
    Generates a structured dataset summary using the OpenAI API.

    Args:
        statistical_summary (str): Statistical summary of the dataset.

    Returns:
        SummaryOutput: A structured summary containing dataset insights and key metrics.
    """
    prompt = SUMMARY_PROMPT_TEMPLATE.format(statistical_summary=statistical_summary)
    try:
        logging.info("Requesting dataset summary from OpenAI...")

        # Retry-enabled API call
        response = call_openai_api(prompt)

        # Log the raw response from OpenAI for debugging
        logging.info("Raw LLM response: %s", response.json())

        logging.info("Successfully received structured response.")
        return response

    except Exception as e:
        logging.error("Error generating summary: %s", e)
        raise ValueError("Failed to generate summary using OpenAI.") from e
