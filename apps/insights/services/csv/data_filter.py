# apps/insights/services/csv/data_filter.py
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def filter_data(df, start_date):
    """
    Filter the DataFrame into two weeks based on the start_date.

    Args:
        df (pd.DataFrame): Input DataFrame to filter.
        start_date (str): Start date for filtering (YYYY-MM-DD).

    Returns:
        tuple: Two DataFrames (Week 1, Week 2).
    """
    logging.info("Filtering data for organic traffic...")
    organic_df = df[df["source"] == "organic"]
    if organic_df.empty:
        raise ValueError("No data found for organic traffic.")

    # Define date ranges
    logging.info(f"Calculating date ranges from start_date: {start_date}")
    start_date = pd.to_datetime(start_date)
    end_date_week1 = start_date + pd.Timedelta(days=6)  # Week 1 range
    start_date_week2 = start_date + pd.Timedelta(days=7)  # Week 2 range
    end_date_week2 = start_date + pd.Timedelta(days=13)  # Week 2 range end

    # Filter Week 1
    logging.info(f"Filtering Week 1: {start_date.date()} to {end_date_week1.date()}")
    week1_df = organic_df[
        (organic_df["date"] >= start_date) & (organic_df["date"] <= end_date_week1)
    ]
    if week1_df.empty:
        raise ValueError("No data found for Week 1.")

    # Log filtered Week 1 data
    logging.info(f"Week 1 Data (Rows: {len(week1_df)}):\n{week1_df}")

    # Filter Week 2
    logging.info(
        f"Filtering Week 2: {start_date_week2.date()} to {end_date_week2.date()}"
    )
    week2_df = organic_df[
        (organic_df["date"] >= start_date_week2)
        & (organic_df["date"] <= end_date_week2)
    ]
    if week2_df.empty:
        raise ValueError("No data found for Week 2.")

    # Log filtered Week 2 data
    logging.info(f"Week 2 Data (Rows: {len(week2_df)}):\n{week2_df}")

    return week1_df, week2_df
