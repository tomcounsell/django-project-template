from apps.insights.tasks import schedule_summary_tasks
from datetime import datetime

# Provide the start_date as a string
start_date = "2024-01-15"  # Replace with your desired date
schedule_summary_tasks(start_date)


from apps.insights.services.app_pipeline import generate_comparison
from datetime import datetime

# Provide the start_date as a string
start_date = "2024-01-15"  # Replace with your desired date
generate_comparison(start_date)
