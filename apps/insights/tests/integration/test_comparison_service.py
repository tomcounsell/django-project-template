# apps/insights/tests/test_comparison_service.py

import pytest
from apps.insights.services.comparison_service import process_comparison
from apps.insights.services.openai.schemas import ComparisonOutput, KeyMetricComparison


def test_process_comparison():
    """
    Test the comparison service using mock structured data for Week 1 and Week 2.
    Prints the output for manual verification.
    """
    # Week 1 structured data
    data_summary1 = {
        "dataset_summary": """
        The dataset covers a 7-day period and encapsulates web analytics data, reflecting user engagement on a website.
        Key metrics include the total number of sessions, users, new users, pageviews, as well as specific engagement metrics 
        such as pages per session, average session duration, bounce rate, conversion rate, transactions, and revenue.
        Overall, the dataset provides an overview of user interaction, revealing patterns in website traffic and user activity
        over the specified time frame.
        """,
        "key_metrics": [
            {
                "name": "Average Sessions",
                "value": 1543.43,
            },
            {
                "name": "Average Users",
                "value": 1265.14,
            },
            {
                "name": "Average New Users",
                "value": 427.29,
            },
            {
                "name": "Average Pageviews",
                "value": 6225.86,
            },
            {
                "name": "Pages per Session",
                "value": 4.01,
            },
            {
                "name": "Average Session Duration",
                "value": 163.1,
            },
            {
                "name": "Bounce Rate",
                "value": 0.2,
            },
            {
                "name": "Conversion Rate",
                "value": 0.028,
            },
            {
                "name": "Average Transactions",
                "value": 34.14,
            },
            {
                "name": "Average Revenue",
                "value": 1622.53,
            },
        ],
    }

    # Week 2 structured data
    data_summary2 = {
        "dataset_summary": """
        The dataset provides a statistical overview of a website's user interaction over a period of seven days in January 2024,
        from the 8th to the 14th. It includes metrics related to sessions, users, new users, pageviews, pages per session, 
        average session duration, bounce rate, conversion rate, transactions, and revenue. The average daily sessions were 
        approximately 1683, with an average of about 1238 users and around 424 new users daily. The website generated an average 
        of 6892 pageviews per day, with each session lasting around 154 seconds on average. The average bounce rate was about 
        16.06%, and the conversion rate stood at about 4.25%. The site recorded an average of 49 transactions per day, resulting
        in a daily revenue averaging $2087.17.
        """,
        "key_metrics": [
            {
                "name": "Average Sessions",
                "value": 1682.57,
            },
            {
                "name": "Average Users",
                "value": 1237.86,
            },
            {
                "name": "Average New Users",
                "value": 424.14,
            },
            {
                "name": "Average Pageviews",
                "value": 6891.71,
            },
            {
                "name": "Pages per Session",
                "value": 4.07,
            },
            {
                "name": "Average Session Duration",
                "value": 153.88,
            },
            {
                "name": "Bounce Rate",
                "value": 0.1606,
            },
            {
                "name": "Conversion Rate",
                "value": 0.0425,
            },
            {
                "name": "Average Transactions",
                "value": 49.43,
            },
            {
                "name": "Average Revenue",
                "value": 2087.17,
            },
        ],
    }

    try:
        # Process comparison
        result = process_comparison(data_summary1, data_summary2)

        # Verify the output type
        assert isinstance(
            result, ComparisonOutput
        ), "Result is not a ComparisonOutput object."

        # Print comparison summary and key metrics for manual verification
        print("Comparison Summary:")
        print(result.comparison_summary)
        print("\nKey Metrics Comparison:")
        for metric in result.key_metrics_comparison:
            print(
                f"{metric.name}: Week 1 Value = {metric.value1}, Week 2 Value = {metric.value2} ({metric.description})"
            )

        print("Test completed successfully.")

    except Exception as e:
        pytest.fail(f"Comparison service test failed: {e}")
