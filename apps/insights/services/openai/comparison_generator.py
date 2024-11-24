# apps/insights/services/openai/comparison_generator.py

import os
from instructor import from_openai
from openai import OpenAI
from .schemas import ComparisonOutput
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load OpenAI API key
openai_api_key = os.environ.get("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

# Initialize OpenAI client
client = from_openai(OpenAI(api_key=openai_api_key))


def generate_comparison(summary1: str, summary2: str) -> ComparisonOutput:
    """
    Generates a structured comparison between two dataset summaries using the OpenAI API.

    Args:
        summary1 (str): The first dataset summary as a string.
        summary2 (str): The second dataset summary as a string.

    Returns:
        ComparisonOutput: A structured comparison containing a summary, key metrics comparison, and notable trends.
    """
    prompt = f"""
You are a data analyst tasked with comparing two dataset summaries. Here are the summaries:

Summary 1:
{summary1}

Summary 2:
{summary2}

Please provide the comparison in the following JSON format:

{{
    "comparison_summary": "A concise summary of differences and similarities.",
    "key_metrics_comparison": [
        {{
            "name": "Name of Metric",
            "value1": Value from Week 1,
            "value2": Value from Week 2,
            "description": "Description of the observed difference or trend."
        }},
        // Repeat for each key metric
    ],
    "notable_trends": "Any notable trends or patterns observed."
}}

Ensure that:
- All numeric values are provided as numbers (not strings).
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
- The description for each metric explains the difference or trend observed between the two summaries.
"""
    try:
        logging.info("Requesting dataset comparison from OpenAI...")

        # API call with structured output validation
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            response_model=ComparisonOutput,
        )

        # Log the raw response from OpenAI for debugging
        logging.info(f"Raw LLM response: {response.json()}")

        logging.info("Successfully received structured response.")
        return response

    except client.ValidationError as e:
        logging.error(f"Validation error: {e}")
        raise ValueError(f"Validation error: {e}")

    except client.ApiError as e:
        logging.error(f"API error: {e}")
        raise ValueError(f"API error: {e}")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise ValueError(f"Unexpected error: {e}")
