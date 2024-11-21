# apps/insights/services/csv/data_filter.py
import pandas as pd


def filter_data(df, start_date):
    # Filter for organic traffic
    organic_df = df[df["source"] == "organic"]
    if organic_df.empty:
        raise ValueError("No data found for organic traffic.")

    # Define date ranges
    start_date = pd.to_datetime(start_date)
    end_date_week1 = start_date + pd.Timedelta(days=6)  # Week 1 range
    start_date_week2 = start_date + pd.Timedelta(days=7)  # Week 2 range
    end_date_week2 = start_date + pd.Timedelta(days=13)  # Week 2 range end

    # Filter Week 1
    week1_df = organic_df[
        (organic_df["date"] >= start_date) & (organic_df["date"] <= end_date_week1)
    ]
    if week1_df.empty:
        raise ValueError("No data found for Week 1.")

    # Filter Week 2
    week2_df = organic_df[
        (organic_df["date"] >= start_date_week2)
        & (organic_df["date"] <= end_date_week2)
    ]
    if week2_df.empty:
        raise ValueError("No data found for Week 2.")

    return week1_df, week2_df
