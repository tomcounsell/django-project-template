import pandas as pd
from django.conf import settings
import os


def load_csv() -> pd.DataFrame:
    """
    Load the CSV file from the correct location into a Pandas DataFrame.

    Returns:
        pd.DataFrame: Loaded data.
    """
    # Use BASE_DIR to define the correct absolute path to the CSV
    file_path = os.path.join(
        settings.BASE_DIR, "apps", "insights", "data", "ga4_data.csv"
    )
    try:
        df = pd.read_csv(file_path)
        print(
            f"Successfully loaded {file_path}: {len(df)} rows, {len(df.columns)} columns"
        )
        return df
    except Exception as e:
        raise ValueError(f"Error loading CSV file: {e}")
