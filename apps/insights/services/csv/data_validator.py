# apps/insights/services/data_validator.py
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

REQUIRED_COLUMNS = {
    "date",
    "source",
    "sessions",
    "users",
    "new_users",
    "pageviews",
    "pages_per_session",
    "avg_session_duration",
    "bounce_rate",
    "conversion_rate",
    "transactions",
    "revenue",
}


def validate_columns(df):
    # Check for missing required columns
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    logging.info("All required key columns are present.")
