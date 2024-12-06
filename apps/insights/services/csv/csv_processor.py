# apps/insights/services/csv_processor.py
import logging
import pandas as pd  # Import pandas for date processing
from .csv_reader import read_csv
from .data_validator import validate_columns
from .data_cleaner import clean_data
from .data_filter import filter_data
from .data_overview import generate_overview

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CSVProcessor:
    """
    A utility class for processing CSV files with various data manipulation operations.

    This class provides a streamlined workflow for loading, validating, cleaning,
    filtering, and generating overviews of CSV data using Pandas.
    """

    def __init__(self):
        """
        Initialize the CSVProcessor.
        """
        self.df = None  # Placeholder for the DataFrame

    def load(self):
        """
        Load the data from the CSV file into a Pandas DataFrame.
        """
        logging.info("Loading CSV...")
        self.df = read_csv()

    def validate(self):
        """
        Validate that the DataFrame contains all required columns.
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
        Filter the DataFrame for the specified traffic source and week.
        """
        logging.info("Filtering data for traffic source: %s", traffic_source)
        return filter_data(self.df, pd.to_datetime(start_date), traffic_source)

    def generate_overview(self):
        """
        Generate a statistical overview of the filtered DataFrame.
        """
        logging.info("Generating statistical overview...")
        return generate_overview(self.df)
