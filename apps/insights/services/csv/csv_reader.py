# apps/insights/services/csv/csv_reader.py
import pandas as pd


def load_csv() -> pd.DataFrame:
    """
    Load the CSV file from an absolute path into a Pandas DataFrame.

    Returns:
        pd.DataFrame: Loaded data.
    """
    file_path = "/app/apps/insights/data/ga4_data.csv"  # Absolute path inside container
    try:
        print(f"Attempting to load file from: {file_path}")
        df = pd.read_csv(file_path)
        print(
            f"Successfully loaded {file_path}: {len(df)} rows, {len(df.columns)} columns"
        )
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found at: {file_path}")
    except Exception as e:
        raise ValueError(f"Error loading CSV file: {e}")
