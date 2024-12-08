import json
from pathlib import Path
import pytest
from apps.insights.services.openai.summary_generator import generate_summary
from apps.insights.services.openai.schemas import SummaryOutput

# Path to dummy test data
TEST_DATA_FILE = Path("apps/insights/tests/data/overview_2024-01-01.json")


@pytest.fixture
def statistical_overview_str():
    """
    Loads the dummy statistical overview from the JSON file and converts it
    to the `pd.describe().to_string()`-like format for testing.
    """
    with open(TEST_DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Format the data to resemble `pd.describe().to_string()`
    overview_lines = []
    headers = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
    for column, stats in data.items():
        if column != "start_date":  # Exclude start_date
            row = [f"{stats.get(header, '')}" for header in headers]
            overview_lines.append(f"{column:<20} {' '.join(row)}")
    return "\n".join(overview_lines)


def test_generate_summary(statistical_overview_str):
    """
    Tests the `generate_summary` function with a stringified statistical overview.
    """
    # Call the generate_summary function
    response = generate_summary(statistical_overview_str)

    # Validate the response structure
    assert isinstance(
        response, SummaryOutput
    ), "Response is not a valid SummaryOutput instance"
    assert response.dataset_summary, "Dataset summary is missing"
    assert len(response.key_metrics) > 0, "Key metrics are missing"
    assert response.chain_of_thought, "Chain of thought reasoning is missing"

    # Validate key metrics structure
    metric_names = [metric.name for metric in response.key_metrics]
    expected_metrics = [
        "Average Sessions",
        "Average Users",
        "Average New Users",
        "Average Pageviews",
        "Pages per Session",
        "Average Session Duration",
        "Bounce Rate",
        "Conversion Rate",
        "Average Transactions",
        "Average Revenue",
    ]
    assert metric_names == expected_metrics, "Key metrics are not in the expected order"

    print("Test passed successfully.")
