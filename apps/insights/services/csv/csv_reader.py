# apps/insights/services/csv/csv_reader.py
from typing import Optional
import logging
from pathlib import Path
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Default CSV file path
CSV_FILE_PATH = "./apps/insights/data/ga4_data.csv"


def read_csv(file_path: Optional[str] = None, **read_csv_kwargs: dict) -> pd.DataFrame:
    """
    Reads a CSV file into a Pandas DataFrame.

    Args:
        file_path (str): Path to the CSV file. Defaults to `CSV_FILE_PATH`.
        read_csv_kwargs (dict): Additional keyword arguments to pass to `pd.read_csv`.

    Returns:
        pd.DataFrame: DataFrame containing the CSV data.

    Raises:
        FileNotFoundError: If the file does not exist at the specified path.
        ValueError: If there is an error reading the file or processing the content.

    Usage:
        df = read_csv(file_path="path/to/csv_data.csv", sep=";",encoding="utf-8-sig", nrows=100)
    """
    file_path = file_path or CSV_FILE_PATH
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        logging.error("CSV file not found at: %s", file_path_obj)
        raise FileNotFoundError(f"CSV file not found at: {file_path_obj}")

    try:
        logging.info("Loading CSV file from: %s", file_path_obj)
        df = pd.read_csv(file_path_obj, **read_csv_kwargs)
        logging.info(
            "Successfully loaded %s: %d rows, %d columns",
            file_path_obj,
            len(df),
            len(df.columns),
        )
        return df
    except Exception as e:
        logging.error("Error reading CSV file at %s: %s", file_path_obj, e)
        raise ValueError(f"Error reading CSV file at {file_path_obj}: {e}") from e
