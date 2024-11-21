# apps/insights/services/openai/schemas.py
from pydantic import BaseModel, Field, root_validator
from typing import List, Optional


class KeyMetric(BaseModel):
    """
    Represents a single key metric extracted from the dataset summary.
    """

    name: str = Field(
        ..., description="Name of the key metric (e.g., 'Mean', 'Median')."
    )
    value: float = Field(..., description="Numeric value of the key metric.")
    description: Optional[str] = Field(
        None, description="Additional details about the key metric."
    )

    @root_validator
    def validate_key_metric(cls, values):
        name = values.get("name")
        value = values.get("value")
        if not name.strip():
            raise ValueError("Key metric name cannot be empty.")
        if value < 0:
            raise ValueError("Key metric value cannot be negative.")
        return values


class SummaryOutput(BaseModel):
    """
    Structured output for a dataset summary response from the LLM.
    """

    dataset_summary: str = Field(
        ..., description="A concise English summary of the dataset."
    )
    key_metrics: List[KeyMetric] = Field(
        ..., description="List of key metrics extracted from the dataset."
    )

    @root_validator
    def validate_summary(cls, values):
        summary = values.get("dataset_summary")
        if len(summary) > 1000:
            raise ValueError(
                "Dataset summary exceeds the maximum allowed length (1000 characters)."
            )
        if not summary.strip():
            raise ValueError("Dataset summary cannot be empty.")
        return values
