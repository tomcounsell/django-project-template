# apps/insights/services/csv/data_cleaner.py
import logging
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def detect_date_column(df: pd.DataFrame) -> str:
    """
    Dynamically detect the date column in a pandas DataFrame.
    """
    date_columns = [col for col in df.columns if "date" in col.lower()]
    if len(date_columns) == 0:
        raise ValueError("No date column detected in the dataset.")
    if len(date_columns) > 1:
        raise ValueError(f"Multiple possible date columns found: {date_columns}")
    logging.info(f"Date column detected: {date_columns[0]}")
    return date_columns[0]


def standardize_date_format(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """
    Standardize the date column to a consistent datetime format.
    """
    try:
        df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
        if df[date_column].isna().any():
            raise ValueError(f"Invalid or unparseable dates in column '{date_column}'.")
        # Removed the following line to keep 'date' as datetime
        # df[date_column] = df[date_column].dt.strftime("%Y-%m-%d")
        logging.info(
            f"Dates standardized to datetime format in column '{date_column}'."
        )
        return df
    except Exception as e:
        raise ValueError(f"Error standardizing date column: {e}")


def ensure_datetime_format(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """
    Ensure the specified column is in datetime format.
    """
    try:
        df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
        if df[date_column].isna().any():
            raise ValueError(f"Invalid or unparseable dates in column '{date_column}'.")
        logging.info(f"Date column '{date_column}' confirmed as datetime format.")
        return df
    except Exception as e:
        raise ValueError(f"Error ensuring datetime format: {e}")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform the full data cleaning process on the input DataFrame.
    """
    date_column = detect_date_column(df)
    df = standardize_date_format(df, date_column)
    df = ensure_datetime_format(df, date_column)
    return df
