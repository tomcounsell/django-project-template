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
    The following is a statistical summary of a dataset:

    {statistical_summary}

    Please:
    1. Write a concise plain English summary of the dataset.
    2. Highlight the key metrics in a structured format.
    """
    try:
        logging.info("Requesting dataset summary from OpenAI...")

        # API call with structured output validation
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            response_model=SummaryOutput,
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
