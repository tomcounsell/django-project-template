from pydantic import BaseModel
from typing import List, Dict, Optional


class SummaryOutput(BaseModel):
    label: str
    plain_summary: str
    key_metrics: Dict[str, float]
    metadata: Optional[Dict[str, str]]


class ComparisonOutput(BaseModel):
    summary_1_label: str
    summary_2_label: str
    comparison_result: Dict[str, float]
    comparison_type: str
