# apps/insights/tests/test_comparison_generator.py

import pytest
from apps.insights.services.openai.comparison_generator import generate_comparison
from apps.insights.services.openai.schemas import ComparisonOutput, KeyMetricComparison


def test_generate_comparison():
    """
    Test the generate_comparison function using two pre-formatted dataset summary strings.
    Prints the output for manual verification.
    """
    # Pre-formatted dataset summaries
    summary1 = """
    The dataset covers a 7-day period and encapsulates web analytics data, reflecting user engagement on a website.
    Key metrics include the total number of sessions, users, new users, pageviews, as well as specific engagement metrics 
    such as pages per session, average session duration, bounce rate, conversion rate, transactions, and revenue.
    Overall, the dataset provides an overview of user interaction, revealing patterns in website traffic and user activity
    over the specified time frame.

    Key Metrics:
    - Average Sessions: 1543.43 (The average number of sessions per day over the 7-day period.)
    - Average Users: 1265.14 (The average number of users visiting the site per day.)
    - Average New Users: 427.29 (The average number of new users per day.)
    - Average Pageviews: 6225.86 (The average number of pageviews per day.)
    - Pages per Session: 4.01 (The average number of pages viewed per session.)
    - Average Session Duration: 163.1 (The mean duration of a user session in seconds.)
    - Bounce Rate: 0.2 (The percentage of visitors who leave after viewing only one page.)
    - Conversion Rate: 0.028 (The proportion of users who completed a desired action.)
    - Average Transactions: 34.14 (The average number of transactions per day.)
    - Average Revenue: 1622.53 (The average revenue generated per day.)
    """

    summary2 = """
    The dataset provides a statistical overview of a website's user interaction over a period of seven days in January 2024,
    from the 8th to the 14th. It includes metrics related to sessions, users, new users, pageviews, pages per session, 
    average session duration, bounce rate, conversion rate, transactions, and revenue. The average daily sessions were 
    approximately 1683, with an average of about 1238 users and around 424 new users daily. The website generated an average 
    of 6891.71 pageviews per day, with each session lasting around 154 seconds on average. The average bounce rate was about 
    16.06%, and the conversion rate stood at about 4.25%. The site recorded an average of 49 transactions per day, resulting
    in a daily revenue averaging $2087.17.

    Key Metrics:
    - Average Sessions: 1682.57 (The average number of sessions per day.)
    - Average Users: 1237.86 (The average number of users per day.)
    - Average New Users: 424.14 (The average number of new users per day.)
    - Average Pageviews: 6891.71 (The average number of pageviews per day.)
    - Pages per Session: 4.07 (The average number of pages viewed per session.)
    - Average Session Duration: 153.88 (The average duration of a session in seconds.)
    - Bounce Rate: 0.1606 (The average bounce rate, representing the percentage of single-page visits.)
    - Conversion Rate: 0.0425 (The average conversion rate calculated as the percentage of sessions that result in a transaction.)
    - Average Transactions: 49.43 (The average number of transactions per day.)
    - Average Revenue: 2087.17 (The average daily revenue in USD.)
    """

    try:
        # Call the generator
        result = generate_comparison(summary1, summary2)

        # Verify the output type
        assert isinstance(
            result, ComparisonOutput
        ), "Result is not a ComparisonOutput object."

        # Log and print results for manual verification
        print("Comparison Summary:")
        print(result.comparison_summary)
        print("\nKey Metrics Comparison:")
        for metric in result.key_metrics_comparison:
            print(
                f"{metric.name}: "
                f"Week 1 Value = {metric.value1}, "
                f"Week 2 Value = {metric.value2} "
                f"({metric.description})"
            )

        # Removed the check for 'notable_trends' since it no longer exists
        # if result.notable_trends:
        #     print("\nNotable Trends:")
        #     print(result.notable_trends)

        print("Test completed successfully.")

    except Exception as e:
        pytest.fail(f"Comparison generator test failed: {e}")
