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
        summary1 (str): The first dataset summary.
        summary2 (str): The second dataset summary.

    Returns:
        ComparisonOutput: A structured comparison containing a summary, key metrics comparison, and notable trends.
    """
    prompt = f"""
    You are a data analyst tasked with comparing two dataset summaries. Here are the summaries:

    Summary 1:
    {summary1}

    Summary 2:
    {summary2}

    Please:
    1. Provide a concise summary of the differences and similarities between the two summaries.
    2. Highlight key metrics where differences or trends are observed, structured as:
        - Name of Metric
        - Value from Summary 1
        - Value from Summary 2
        - Description of the observed difference or trend.
    3. Mention any notable trends or patterns observed during the comparison.
    """
    try:
        logging.info("Requesting dataset comparison from OpenAI...")

        # API call with structured output validation
        response = client.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            response_format=ComparisonOutput,
        )

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
