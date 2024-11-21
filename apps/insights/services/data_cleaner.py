import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Detect the date column dynamically
def detect_date_column(df):
    # Identify the column containing "date" (case-insensitive)
    date_columns = [col for col in df.columns if "date" in col.lower()]
    if len(date_columns) == 0:
        raise ValueError("No date column detected in the dataset.")
    if len(date_columns) > 1:
        raise ValueError(f"Multiple possible date columns found: {date_columns}")
    logging.info(f"Date column detected: {date_columns[0]}")
    return date_columns[0]


# Standardize the format of the date column
def standardize_date_format(df, date_column):
    try:
        # Convert to datetime and handle errors
        df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
        if df[date_column].isna().any():
            raise ValueError(f"Invalid or unparseable dates in column '{date_column}'.")
        # Format the date to 'YYYY-MM-DD'
        df[date_column] = df[date_column].dt.strftime("%Y-%m-%d")
        logging.info(
            f"Dates standardized to 'YYYY-MM-DD' format in column '{date_column}'."
        )
        return df
    except Exception as e:
        raise ValueError(f"Error standardizing date column: {e}")


# Perform the full data cleaning process
def clean_data(df):
    # Detect the date column
    date_column = detect_date_column(df)

    # Standardize the date format
    df = standardize_date_format(df, date_column)

    # Return the cleaned DataFrame
    return df
