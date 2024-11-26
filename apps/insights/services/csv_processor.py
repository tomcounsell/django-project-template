# apps/insights/services/csv_processor.py
import logging
import pandas as pd  # Import pandas for date processing
from .csv.csv_reader import load_csv
from .csv.data_validator import validate_columns
from .csv.data_cleaner import clean_data
from .csv.data_filter import filter_data
from .csv.data_overview import generate_overview

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CSVProcessor:
    def __init__(self):
        """
        Initialize the CSVProcessor.
        """
        self.df = None  # Placeholder for the loaded DataFrame

    def load(self):
        """
        Load the CSV file into a Pandas DataFrame.
        """
        logging.info("Loading CSV...")
        self.df = load_csv()

    def validate(self):
        """
        Validate that the CSV contains all required columns.
        """
        logging.info("Validating CSV columns...")
        validate_columns(self.df)

    def clean(self):
        """
        Clean the DataFrame by standardizing and formatting columns.
        """
        logging.info("Cleaning data...")
        self.df = clean_data(self.df)

    def filter(self, start_date: str, week_number: int):
        """
        Filters the data for the current (1) or past (2) week using the data_filter module.

        Args:
            start_date (str): Start date for the dataset (YYYY-MM-DD).
            week_number (int): Week number to filter (1 = current week, 2 = past week).

        Returns:
            pd.DataFrame: Filtered DataFrame for the specified week.
        """
        return filter_data(self.df, start_date, week_number)

    def generate_overview(self, df, label):
        """
        Generate a statistical overview for a single DataFrame.
        """
        logging.info(f"Generating statistical overview for {label}...")
        print(f"\nStatistical Overview - {label}:")
        print(df.describe())
