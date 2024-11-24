# Run this in the Django Python shell inside the Docker container
from apps.insights.services.comparison_service import (
    process_comparison,
    save_comparison_to_database,
    save_comparison_to_file,
)
from apps.insights.models.comparison import Comparison, KeyMetricComparison
from apps.insights.models.summary import Summary
from apps.insights.services.openai.schemas import ComparisonOutput

# Mock structured data for Week 1 and Week 2
data_summary1 = {
    "dataset_summary": """
    The dataset provides a detailed view of website interactions over a period, highlighting user engagement and conversion metrics.
    On average, there were 729 sessions per day, with a significant variance as the minimum was 181 and the maximum 1940 sessions, showing possible peak days or events.
    Users averaged at 584.81 per day, indicating a solid user base, although the new user average was notably lower at 200.76, which could imply either high return rates or less attraction to new users.
    The average pageviews reached 2650.88, suggesting substantial user engagement per session, supported by the average pages per session metric at 3.54.
    The session duration averaged 143.54 seconds, which shows users spend a considerable amount of time engaged per session.
    The bounce rate at 24.62% is relatively low, indicating effective user retention on initial pages. With a conversion rate of 2.64%, there is moderate success in turning interactions into actions.
    Transactions averaged at 15.07 per day, contributing to an average daily revenue of 755.10, indicating satisfactory financial outcomes from the user activities, albeit with room for improvement in conversion efficiency.
    """,
    "key_metrics": [
        {"name": "Average Sessions", "value": 729.0},
        {"name": "Average Users", "value": 584.81},
        {"name": "Average New Users", "value": 200.76},
        {"name": "Average Pageviews", "value": 2650.88},
        {"name": "Pages per Session", "value": 3.54},
        {"name": "Average Session Duration", "value": 143.54},
        {"name": "Bounce Rate", "value": 0.246236},
        {"name": "Conversion Rate", "value": 0.026381},
        {"name": "Average Transactions", "value": 15.07},
        {"name": "Average Revenue", "value": 755.10},
    ],
}

data_summary2 = {
    "dataset_summary": """
    This dataset provides a detailed statistical summary of website performance metrics over a span of 42 days, centered around the mid-January period of 2024.
    The average number of sessions per day is approximately 770, with users averaging nearly 596 and new users being around 207 per day.
    A significant amount of pageviews is recorded, averaging about 2874 daily, complemented by an average of 3.58 pages per session, suggesting reasonable engagement levels.
    The average session lasts around 128 seconds, with a bounce rate of approximately 28%.
    Notably, the conversion rate is relatively low at 2.78%, yet transactions average about 17 per day, indicating that while user acquisition may be moderate, those engaged result in financial transactions amounting to an average daily revenue of $815.
    Variability is considerable across these metrics, particularly with a wide standard deviation in transactions and revenue, suggesting fluctuating daily performance.
    Extremely high maximum values, such as 2138 sessions and a peak revenue of $3277, indicate occasional spikes, likely due to specific events or promotions that temporarily enhanced user engagement and sales figures.
    """,
    "key_metrics": [
        {"name": "Average Sessions", "value": 770.52},
        {"name": "Average Users", "value": 595.93},
        {"name": "Average New Users", "value": 207.38},
        {"name": "Average Pageviews", "value": 2874.48},
        {"name": "Pages per Session", "value": 3.58},
        {"name": "Average Session Duration", "value": 127.56},
        {"name": "Bounce Rate", "value": 0.28},
        {"name": "Conversion Rate", "value": 0.028},
        {"name": "Average Transactions", "value": 16.86},
        {"name": "Average Revenue", "value": 814.92},
    ],
}

# Run the comparison service
try:
    # Ensure you have at least two summary objects in your database for testing
    summary1 = Summary.objects.first()
    summary2 = Summary.objects.last()

    if not summary1 or not summary2:
        raise ValueError(
            "Not enough summaries in the database. Please ensure two exist."
        )

    # Process the comparison
    comparison_result = process_comparison(data_summary1, data_summary2)

    # Save the comparison to the database
    save_comparison_to_database(summary1.id, summary2.id, comparison_result)

    # Optionally save the comparison to a JSON file
    save_comparison_to_file(comparison_result, summary1.id, summary2.id)

    # Output results for manual verification
    print("Comparison Summary:")
    print(comparison_result.comparison_summary)
    print("\nKey Metrics Comparison:")
    for metric in comparison_result.key_metrics_comparison:
        print(
            f"{metric.name}: Week 1 Value = {metric.value1}, Week 2 Value = {metric.value2} ({metric.description})"
        )

    # Verify database entries
    print("Comparison in DB:", Comparison.objects.all())
    print("Key Metric Comparisons in DB:", KeyMetricComparison.objects.all())

except Exception as e:
    print(f"Error during test: {e}")
