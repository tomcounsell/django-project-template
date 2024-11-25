from apps.insights.services.comparison_service import process_comparison

# Mock structured data for Week 1
data_summary1 = {
    "dataset_summary": "The dataset encompasses 42 entries of web analytics data, revealing user interaction trends. On average, there are 771 sessions and 596 users daily, indicating a moderate level of engagement. Notably, only 207 of these users are new, suggesting a strong returning customer base. Pageviews average at 2874, with users exploring approximately 3.58 pages per session. Sessions typically last around 128 seconds, reflecting concentrated user engagement within short spans. The bounce rate is 27.8%, showing a fair amount of single-page visits, and the conversion rate stands at 2.78%. Transaction volumes average at 17 daily with a corresponding revenue of $814.92. Anomalies include a maximum session count of 2138 and revenue peaking at $3277.14, pointing towards specific days of peak user interest or promotional events. Such peaks offer opportunities for strategic marketing refinements.",
    "key_metrics": [
        {"name": "Average Sessions", "value": 770.52},
        {"name": "Average Users", "value": 595.93},
        {"name": "Average New Users", "value": 207.38},
        {"name": "Average Pageviews", "value": 2874.48},
        {"name": "Pages per Session", "value": 3.58},
        {"name": "Average Session Duration", "value": 127.56},
        {"name": "Bounce Rate", "value": 0.2781},
        {"name": "Conversion Rate", "value": 0.0278},
        {"name": "Average Transactions", "value": 16.86},
        {"name": "Average Revenue", "value": 814.92},
    ],
}

# Mock structured data for Week 2
data_summary2 = {
    "dataset_summary": "The dataset provides an overview of web analytics over 43 days, indicating user engagement and conversion metrics. On average, there are 923.84 sessions per day, with a majority being returning users, as indicated by the 746.65 average users, and 254.28 being new. Pageviews average at 3168.86 daily, suggesting moderate user activity per session with 3.45 pages viewed on average. The average session duration of 125.70 seconds implies brief engagement per visit. Bounce rate is 25.79%, showing a relatively engaged audience, given industry ranges. The conversion rate stands at 2.52%, with an average of 18.67 transactions and revenue of $830.98 daily. Notably, there's a high variance in sessions and revenue, evident from the maximum values reaching 7619 sessions and $5099.72 in revenue, pointing to significant peaks on specific days.",
    "key_metrics": [
        {"name": "Average Sessions", "value": 923.84},
        {"name": "Average Users", "value": 746.65},
        {"name": "Average New Users", "value": 254.28},
        {"name": "Average Pageviews", "value": 3168.86},
        {"name": "Pages per Session", "value": 3.45},
        {"name": "Average Session Duration", "value": 125.7},
        {"name": "Bounce Rate", "value": 0.2579},
        {"name": "Conversion Rate", "value": 0.0252},
        {"name": "Average Transactions", "value": 18.67},
        {"name": "Average Revenue", "value": 830.98},
    ],
}

# Run the comparison service
comparison_result = process_comparison(data_summary1, data_summary2)

# Output the comparison results
print("Comparison Summary:")
print(comparison_result.comparison_summary)

print("\nKey Metrics Comparison:")
for metric in comparison_result.key_metrics_comparison:
    print(
        f"{metric.name}: Week 1 = {metric.value1}, Week 2 = {metric.value2} ({metric.description})"
    )
