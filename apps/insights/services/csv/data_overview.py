# apps/insights/services/csv/data_overview.py
import pandas as pd


def generate_overview(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a statistical overview for the given DataFrame.

    Args:
        df (DataFrame): The DataFrame to generate an overview for.
    """
    statistical_overview = df.describe()
    print(statistical_overview)
    return statistical_overview
