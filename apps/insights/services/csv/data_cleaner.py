# apps/insights/services/csv/data_cleaner.py
from typing import List
import logging
import pandas as pd
from apps.insights.services.utils.data_utils import validate_dataframe

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def detect_date_column(df: pd.DataFrame) -> str:
    """
    Detects the date column in a pandas DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to inspect for a date column.

    Returns:
        str: The name of the detected date column.

    Raises:
        ValueError: If no date column is detected or if multiple columns
        contain "date" in their name.//
    """
    # Validate that input is a DataFrame
    validate_dataframe(df)

    # Find columns with "date" in their names (case-insensitive)
    date_columns: List[str] = [col for col in df.columns if "date" in col.lower()]

    if len(date_columns) == 0:
        logging.error("No date column detected in the dataset.")
        raise ValueError("No date column detected in the dataset.")

    if len(date_columns) > 1:
        logging.error(
            "Multiple possible date columns found: %s", ", ".join(date_columns)
        )
        raise ValueError(
            f"Multiple possible date columns found: {', '.join(date_columns)}"
        )

    logging.info("Date column detected: %s", date_columns[0])
    return date_columns[0]


def standardize_date_format(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """
    Standardizes the date column to a consistent datetime format.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        date_column (str): The name of the column to standardize.

    Returns:
        pd.DataFrame: The DataFrame with the standardized date column.

    Raises:
        ValueError: If invalid or unparseable dates are found.
    """
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    if df[date_column].isna().any():
        raise ValueError(f"Invalid or unparseable dates in column '{date_column}'.")
    logging.info("Dates standardized to datetime format in column '%s'", date_column)
    return df


def ensure_datetime_format(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    """
    Ensures the specified column is in datetime format.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        date_column (str): The name of the column to validate and ensure is in datetime format.

    Returns:
        pd.DataFrame: The DataFrame with the specified column converted to datetime format.

    Raises:
        ValueError: If the column contains invalid or unparseable dates.
    """
    # Convert column to datetime with coercion for invalid entries
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")

    # Check for invalid or missing dates
    if df[date_column].isna().any():
        invalid_count = df[date_column].isna().sum()
        logging.error(
            "Column '%s' contains %d invalid or unparseable date entries.",
            date_column,
            invalid_count,
        )
        raise ValueError(
            f"Column '{date_column}' contains {invalid_count} invalid or unparseable dates."
        )

    logging.info("Date column '%s' confirmed as datetime format.", date_column)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs the full data cleaning process on the input DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to clean.

    Returns:
        pd.DataFrame: The cleaned DataFrame with a standardized date column.
    """
    # Validate the DataFrame
    validate_dataframe(df)

    # Perform data cleaning steps
    date_column = detect_date_column(df)
    df = standardize_date_format(df, date_column)
    df = ensure_datetime_format(df, date_column)
    return df
