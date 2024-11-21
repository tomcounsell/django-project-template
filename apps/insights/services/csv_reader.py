# apps/insights/services/csv_reader.py
import pandas as pd  # Missing import added


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load a CSV file into a Pandas DataFrame.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded data.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded CSV: {len(df)} rows, {len(df.columns)} columns")
        return df
    except Exception as e:
        raise ValueError(f"Error loading CSV file: {e}")
