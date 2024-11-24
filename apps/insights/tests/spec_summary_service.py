# Run this in the Django Python shell inside the Docker container
from apps.insights.services.summary_service import process_week
from apps.insights.models.summary import Summary, KeyMetric

# Define the test parameters
start_date = "2024-01-01"  # Replace with your test date
week_number = 1  # Testing for Week 1

# Call the summary service
try:
    result = process_week(start_date, week_number)
    print("LLM Summary Output:")
    print(result.dataset_summary)

    # Check database entries
    print("Summaries in DB:")
    for summary in Summary.objects.all():
        print(summary)

    print("Key Metrics in DB:")
    for metric in KeyMetric.objects.all():
        print(metric)

except Exception as e:
    print(f"Error during test: {e}")
