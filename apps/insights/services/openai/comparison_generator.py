# apps/insights/services/openai/comparison_generator.py

from django.conf import settings
from instructor import from_openai
from openai import OpenAI
from .schemas import ComparisonOutput
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

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
    prompt = f"""
You are a data analyst tasked with comparing two dataset summaries. Here are the summaries:

{summary1} is the current week.

{summary2} is the week prior.

Think step-by-step to explain your reasoning for the comparison, and include this explanation in the field `chain_of_thought`.

Please provide the comparison in the following JSON format:

{{
    "comparison_summary": "A comprehensive summary of differences and similarities between the current week and previous week, including notable trends and observations.
    Ensure that:
        - Maximum length is 180 words.
        - Refer to the summaries as 'this week' and 'the previous week' in your summary.
        - Use precise verbal descriptions to describe the observed differences or trends between the current week and the previous week data in your summary.
        - Mention up to three salient numerical values in your summary.
        - Commas should be used in numerical values to separate thousands in your summary.",
    "key_metrics_comparison": [
        {{
            "name": "Name of Metric",
            "value1": Value from current week,
            "value2": Value from previous week,
            "description": "Description of observed difference or trend between the previous week and the current week, including specific figures and percentages where appropriate."
        }}
        // Repeat for each key metric
    ],
    "chain_of_thought": "Step-by-step reasoning explaining how the comparison summary and key metrics were derived."
}}

Ensure that:
- Numerical values for value1 and value2 are provided as numbers (not strings) for each metric.
- The key_metrics_comparison includes the following metrics in this order:
    - "Average Sessions"
    - "Average Users"
    - "Average New Users"
    - "Average Pageviews"
    - "Pages per Session"
    - "Average Session Duration"
    - "Bounce Rate"
    - "Conversion Rate"
    - "Average Transactions"
    - "Average Revenue"
- The description for each metric explains the difference or trend observed between the current week and one week prior, using precise figures (e.g., differences, statistics, percentages).
- Refer to the summaries as "this week" and "the previous week" in your descriptions.
"""
    try:
        logging.info("Requesting dataset comparison from OpenAI...")

        # Retry-enabled API call
        response = call_openai_api(prompt)

        # Log the raw response from OpenAI for debugging
        logging.info(f"Raw LLM response: {response.json()}")

        logging.info("Successfully received structured response.")
        return response

    except Exception as e:
        logging.error(f"Error generating comparison: {e}")
        raise ValueError("Failed to generate comparison using OpenAI.") from e
