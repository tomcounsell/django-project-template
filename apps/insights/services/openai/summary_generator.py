# apps/insights/services/openai/summary_generator.py

import os
from instructor import from_openai
from openai import OpenAI
from .schemas import SummaryOutput
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load OpenAI API key
openai_api_key = os.environ.get("OPENAI_API_KEY")  # Use os.environ.get()

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

# Initialize OpenAI client
client = from_openai(OpenAI(api_key=openai_api_key))


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
        - Commas are used in numerical values to separate thousands.",
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

        # API call with structured output validation
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            response_model=SummaryOutput,
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
