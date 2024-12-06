# apps/insights/services/csv/data_overview.py
import logging
import pandas as pd


def generate_overview(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a statistical overview for the given DataFrame.

    Args:
        df (DataFrame): The DataFrame to generate an overview for.
    """
    print(df.describe())
    return df
