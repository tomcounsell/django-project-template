from apps.insights.tasks_chain import schedule_summary_tasks
from datetime import datetime

# Provide the start_date as a string
start_date = "2024-01-01"  # Replace with your desired date
schedule_summary_tasks(start_date)
