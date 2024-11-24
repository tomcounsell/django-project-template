# Run this in the Django Python shell inside the Docker container
from apps.insights.services.summary_service import process_week
from apps.insights.models.summary import Summary, KeyMetric

# Replace with your test CSV file path and start_date
file_path = (
    "apps/insights/data/ga4_data.csv"  # Ensure the path is accessible in the container
)
start_date = "2024-01-01"  # Replace with your test date
week_number = 1  # Testing for Week 1

# Call the service
try:
    result = process_week(file_path, start_date, week_number)
    print("LLM Summary Output:", result.dataset_summary)

    # Check database entries
    print("Summaries in DB:", Summary.objects.all())
    print("Key Metrics in DB:", KeyMetric.objects.all())

except Exception as e:
    print(f"Error during test: {e}")
