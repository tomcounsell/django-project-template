import pandas as pd

REQUIRED_COLUMNS = {"date", "source", "sessions", "users", "revenue"}


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


def validate_columns(df: pd.DataFrame):
    """
    Validate that the DataFrame contains all required columns.

    Args:
        df (pd.DataFrame): DataFrame to validate.

    Raises:
        ValueError: If required columns are missing.
    """
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    print("All required columns are present.")
