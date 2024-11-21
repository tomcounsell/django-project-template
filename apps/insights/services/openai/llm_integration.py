# apps/insights/services/openai/llm_integration.py
from decouple import config
import instructor
from openai import OpenAI
from typing import List
from .schemas import SummaryOutput  # Import the updated SummaryOutput model

# Load the OpenAI API key from environment variables
openai_api_key = config("OPENAI_API_KEY")

# Initialize OpenAI client with Instructor
client = instructor.from_openai(OpenAI(api_key=openai_api_key))


def generate_summary(statistical_summary: str) -> SummaryOutput:
    """
    Generates a structured dataset summary using the OpenAI API.

    Args:
        statistical_summary (str): The statistical summary of the dataset.

    Returns:
        SummaryOutput: The structured output containing a dataset summary and key metrics.
    """
    prompt = f"""
    The following is a statistical summary of a dataset:

    {statistical_summary}

    Please:
    1. Write a concise summary of the dataset.
    2. Highlight the key metrics.
    """
    try:
        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": prompt}],
            response_model=SummaryOutput,  # Use the updated SummaryOutput model for validation
        )
        return response

    except instructor.ValidationError as e:
        raise ValueError(f"Validation Error: {e}")

    except instructor.ApiError as e:
        raise ValueError(f"API Error: {e}")

    except Exception as e:
        raise ValueError(f"Unexpected Error: {e}")
