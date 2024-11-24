# apps/insights/services/openai/schemas.py

from pydantic import BaseModel, Field
from typing import List


class KeyMetric(BaseModel):
    """
    Represents a single key metric extracted from the dataset summary.
    """

    name: str
    value: float
    description: str

    @classmethod
    def ordered_metrics(cls) -> List["KeyMetric"]:
        """
        Defines the exact order and expected names for key metrics.
        """
        return [
            cls(
                name="Average Sessions",
                value=0,
                description="The mean number of sessions per day.",
            ),
            cls(
                name="Average Users",
                value=0,
                description="The mean number of users per day.",
            ),
            cls(
                name="Average New Users",
                value=0,
                description="The mean number of new users per day.",
            ),
            cls(
                name="Average Pageviews",
                value=0,
                description="The mean number of pageviews per day.",
            ),
            cls(
                name="Pages per Session",
                value=0,
                description="The average number of pages viewed per session.",
            ),
            cls(
                name="Average Session Duration",
                value=0,
                description="The average duration of a session in seconds.",
            ),
            cls(
                name="Bounce Rate",
                value=0,
                description="The average percentage of visitors who leave the site after viewing only one page.",
            ),
            cls(
                name="Conversion Rate",
                value=0,
                description="The average percentage of visitors who completed a desired action.",
            ),
            cls(
                name="Average Transactions",
                value=0,
                description="The mean number of transactions per day.",
            ),
            cls(
                name="Average Revenue",
                value=0,
                description="The average revenue generated per day.",
            ),
        ]

    def validate_name(self) -> bool:
        """
        Ensures that the name of the metric matches one of the expected names.
        """
        expected_names = [metric.name for metric in self.ordered_metrics()]
        if self.name not in expected_names:
            raise ValueError(f"Unexpected metric name: {self.name}")
        return True


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

    def enforce_ordered_metrics(self):
        """
        Enforces that key metrics are in the exact order defined by `KeyMetric.ordered_metrics`.
        """
        ordered_names = [metric.name for metric in KeyMetric.ordered_metrics()]
        self.key_metrics = sorted(
            self.key_metrics,
            key=lambda metric: (
                ordered_names.index(metric.name)
                if metric.name in ordered_names
                else float("inf")
            ),
        )
        # Ensure no unexpected metrics
        for metric in self.key_metrics:
            metric.validate_name()


class KeyMetricComparison(BaseModel):
    """
    Represents a comparison of a key metric between two datasets.
    """

    name: str
    value1: float
    value2: float
    description: str


class ComparisonOutput(BaseModel):
    """
    Structured output for comparing two dataset summaries.
    """

    comparison_summary: str = Field(
        ...,
        description="A concise English summary highlighting differences and similarities between Week 1 and Week 2.",
    )
    key_metrics_comparison: List[KeyMetricComparison] = Field(
        ...,
        description="Key metrics with values from both weeks and descriptions of differences.",
    )
