# apps/insights/services/csv/data_overview.py
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def generate_overview(df: pd.DataFrame, label: str):
    """
    Generates a statistical overview for the given DataFrame.

    Args:
        df (DataFrame): The DataFrame to generate an overview for.
        label (str): A label for logging (e.g., Week 1 or Week 2).
    """
    logging.info(f"Generating statistical overview for {label}...")
    print(f"\nStatistical Overview - {label}:")
    print(df.describe())
