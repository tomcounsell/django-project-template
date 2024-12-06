# apps/insights/services/csv_processor.py
import logging
import pandas as pd  # Import pandas for date processing
from .csv_reader import load_csv
from .data_validator import validate_columns
from .data_cleaner import clean_data
from .data_filter import filter_data
from .data_overview import generate_overview

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

    def filter(self, start_date: str, traffic_source: str = "organic"):
        """
        Filter the data for the specified traffic source and week.
        """
        logging.info(f"Filtering data for traffic source: {traffic_source}")
        return filter_data(self.df, pd.to_datetime(start_date), traffic_source)

    def generate_overview(self, df, label):
        """
        Generate a statistical overview for a single DataFrame.
        """
        logging.info(f"Generating statistical overview for {label}...")
        print(f"\nStatistical Overview - {label}:")
        print(df.describe())
