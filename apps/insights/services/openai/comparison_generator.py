# apps/insights/services/openai/comparison_generator.py

import logging
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

# Load OpenAI API key from settings
openai_api_key = settings.OPENAI_API_KEY

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in Django settings.")

# Initialize OpenAI client
client = from_openai(OpenAI(api_key=openai_api_key))


# Retry logic for transient errors
@retry(
    stop=stop_after_attempt(settings.OPENAI_RETRY_ATTEMPTS),
    wait=wait_exponential(
        multiplier=settings.OPENAI_RETRY_WAIT_MULTIPLIER,
        min=settings.OPENAI_RETRY_WAIT_MIN,
        max=settings.OPENAI_RETRY_WAIT_MAX,
    ),
)
def call_openai_api(prompt: str) -> ComparisonOutput:
    """
    Makes a call to the OpenAI API with a retry mechanism for transient errors.

    Args:
        prompt (str): The input prompt for the OpenAI model.

    Returns:
        ComparisonOutput: A structured comparison containing a summary and key metrics comparison.
    """
    try:
        logging.debug(f"Sending prompt to OpenAI: {prompt}")
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            response_model=ComparisonOutput,
        )
        logging.debug(f"OpenAI Response: {response}")
        return response
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
        logging.debug(f"Formatted prompt:\n{prompt}")

        # Retry-enabled API call
        response = call_openai_api(prompt)

        # Log the successful response
        logging.info("Successfully received structured response.")
        logging.debug(f"Structured response:\n{response.model_dump()}")

        return response

    except Exception as e:
        logging.error(f"Error generating comparison: {e}")
        raise ValueError("Failed to generate comparison using OpenAI.") from e
