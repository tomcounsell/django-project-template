# apps/insights/services/csv/csv_reader.py
import pandas as pd

CSV_FILE_PATH = "/app/apps/insights/data/ga4_data.csv"


def load_csv(file_path: str = CSV_FILE_PATH) -> pd.DataFrame:
    """
    Load the CSV file into a Pandas DataFrame.
    """
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
