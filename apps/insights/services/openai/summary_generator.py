# apps/insights/services/openai/summary_generator.py

import os
from django.conf import settings
from instructor import from_openai
from openai import OpenAI
from .schemas import SummaryOutput
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
        logging.error(f"Error during OpenAI API call: {e}")
        raise


def generate_summary(statistical_summary: str) -> SummaryOutput:
    """
    Generates a structured dataset summary using OpenAI API.

    Args:
        statistical_summary (str): Statistical summary of the dataset.

    Returns:
        SummaryOutput: A structured summary containing dataset insights and key metrics.
    """
    prompt = f"""
You are a data analyst tasked with summarizing a dataset. The following is a statistical summary of the dataset:

{statistical_summary}

Please provide the summary in the following JSON format:

{{
    "dataset_summary": "A concise, insightful summary highlighting significant findings, trends, or patterns observed in the data. Mention any notable data or anomalies in the key metrics, providing context by referencing the actual values and what they indicate about user behavior or performance metrics.
    Ensure that:
        - Commas are used in numerical values to separate thousands in the summary.",
    "key_metrics": [
        {{
            "name": "Name of Metric",
            "value": Numeric value
        }}
        // Repeat for each key metric
    ]
}}

Ensure that:
- All numeric values are provided as numbers (not strings).
- The key_metrics include the following metrics in this order:
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
- Do not include descriptions for the key metrics.
- Focus on delivering specific insights derived from the data.
- Avoid generic statements or repeating information without analysis.
"""
    try:
        logging.info("Requesting dataset summary from OpenAI...")

        # Retry-enabled API call
        response = call_openai_api(prompt)

        # Log the raw response from OpenAI for debugging
        logging.info(f"Raw LLM response: {response.json()}")

        logging.info("Successfully received structured response.")
        return response

    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        raise ValueError("Failed to generate summary using OpenAI.") from e
