import logging
import pandas as pd


def filter_data(df, start_date: str, week_number: int):
    """
    Filters the data for the current (1) or past (2) week.

    Args:
        df (pd.DataFrame): DataFrame containing the data to filter.
        start_date (str): Start date for the dataset (YYYY-MM-DD).
        week_number (int): Week number to filter (1 = current week, 2 = past week).

    Returns:
        pd.DataFrame: Filtered DataFrame for the specified week.
    """
    logging.info(f"Filtering data for Week {week_number}...")
    start_date = pd.to_datetime(start_date)

    # Week 1: No date adjustment needed
    week_start = start_date
    week_end = start_date + pd.Timedelta(days=6)

    # If week_number == 2, assume start_date has already been adjusted in process_week
    filtered_df = df[(df["date"] >= week_start) & (df["date"] <= week_end)]
    logging.info(f"Filtered Week {week_number} Data: {len(filtered_df)} rows.")
    return filtered_df
