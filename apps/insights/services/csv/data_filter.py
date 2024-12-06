# apps/insights/services/csv/data_filter.py
import logging
import pandas as pd


def filter_data(df, start_date: pd.Timestamp, traffic_source: str):
    """
    Filters the data for a specified traffic source
    within a 7-day period starting from the given date.

    Args:
        df (pd.DataFrame): DataFrame containing the data to filter.
        start_date (pd.Timestamp): Start date for the dataset (YYYY-MM-DD).
        traffic_source (str): Traffic source to filter (e.g., "organic").

    Returns:
        pd.DataFrame: Filtered DataFrame for the specified traffic source in the 7-day period.
    """
    logging.info(f"Filtering '{traffic_source}' traffic starting from {start_date}...")

    # Convert start_date to datetime
    end_date = start_date + pd.Timedelta(days=6)

    # Filter for the specified traffic source
    filtered_df = df[df["source"] == traffic_source]
    if filtered_df.empty:
        raise ValueError(f"No data found for traffic source '{traffic_source}'.")

    # Apply date range filter
    filtered_df = filtered_df[
        (filtered_df["date"] >= start_date) & (filtered_df["date"] <= end_date)
    ]
    if filtered_df.empty:
        raise ValueError(
            f"No data found in the 7-day period starting from {start_date}."
        )

    # Log filtered data
    logging.info(f"Filtered Data (Rows: {len(filtered_df)}):\n{filtered_df}")
    return filtered_df
