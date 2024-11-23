# apps/insights/services/csv_processor.py
import logging
from .csv.csv_reader import load_csv
from .csv.data_validator import validate_columns
from .csv.data_cleaner import clean_data
from .csv.data_filter import filter_data
from .csv.data_overview import generate_overview

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CSVProcessor:
    def __init__(self, file_path: str):
        """
        Initialize the CSVProcessor with the path to the CSV file.
        """
        self.file_path = file_path
        self.df = None  # Placeholder for the loaded DataFrame

    def load(self):
        """
        Load the CSV file into a Pandas DataFrame.
        """
        logging.info("Loading CSV...")
        self.df = load_csv(self.file_path)

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

    def filter(self, start_date: str):
        """
        Filter the data into two weeks based on the start date.
        """
        logging.info("Filtering data into Week 1 and Week 2...")
        return filter_data(self.df, start_date)

    def generate_overviews(self, week1_df, week2_df):
        """
        Generate statistical overviews for the filtered DataFrames.
        """
        logging.info("Generating statistical overviews...")
        generate_overview(week1_df, "Week 1")
        generate_overview(week2_df, "Week 2")

    def process(self, start_date: str):
        try:
            self.load()
            self.validate()
            self.clean()
            week1_df, week2_df = self.filter(start_date)
            self.generate_overviews(week1_df, week2_df)
        except ValueError as e:
            logging.error(f"Processing error: {e}")
            raise
