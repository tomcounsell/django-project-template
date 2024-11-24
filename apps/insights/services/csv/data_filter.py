# apps/insights/services/csv/data_filter.py
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def filter_data(df, start_date):
    """
    Filter the DataFrame for a single 7-day period based on the start_date.

    Args:
        df (pd.DataFrame): Input DataFrame to filter.
        start_date (str): Start date for filtering (YYYY-MM-DD).

    Returns:
        pd.DataFrame: Filtered DataFrame for the 7-day period.
    """
    logging.info("Filtering data for organic traffic...")
    organic_df = df[df["source"] == "organic"]
    if organic_df.empty:
        raise ValueError("No data found for organic traffic.")

    # Define date range
    logging.info(f"Calculating date range from start_date: {start_date}")
    start_date = pd.to_datetime(start_date)
    end_date = start_date + pd.Timedelta(days=6)

    # Filter the 7-day period
    logging.info(f"Filtering data: {start_date.date()} to {end_date.date()}")
    filtered_df = organic_df[
        (organic_df["date"] >= start_date) & (organic_df["date"] <= end_date)
    ]
    if filtered_df.empty:
        raise ValueError("No data found for the specified 7-day period.")

    # Log filtered data
    logging.info(f"Filtered Data (Rows: {len(filtered_df)}):\n{filtered_df}")
    return filtered_df
