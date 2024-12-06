# apps/insights/services/csv/csv_reader.py
import pandas as pd

CSV_FILE_PATH = "/app/apps/insights/data/ga4_data.csv"


def read_csv(file_path: str = CSV_FILE_PATH) -> pd.DataFrame:
    """
    Read the CSV file into a Pandas DataFrame.
    """
    try:
        print(f"Attempting to load file from: {file_path}")
        df = pd.read_csv(file_path)
        print(
            f"Successfully loaded {file_path}: {len(df)} rows, {len(df.columns)} columns"
        )
        return df
    except FileNotFoundError as e:
        raise FileNotFoundError(f"CSV file not found at: {file_path}") from e
    except Exception as e:
        raise ValueError(f"Error reading CSV file at {file_path}: {e}") from e
