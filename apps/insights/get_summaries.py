# apps/insights/get_summaries.py
from .services.csv_reader import load_csv
from .services.data_validator import validate_columns
from .services.data_cleaner import clean_data
from .services.data_filter import filter_data


def main():
    # Resolve the file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "./data/ga4_data.csv")

    # Load the CSV file
    print("Loading CSV...")
    df = load_csv(file_path)

    # Validate all columns
    print("Validating columns...")
    validate_columns(df)

    # Clean the data (date column, etc.)
    print("Cleaning data...")
    df = clean_data(df)

    # Filter the data (1st week, 2nd week)
    print("Filtering data...")
    start_date = "2024-01-01"  # FIXME: Variable input
    week1_df, week2_df = filter_data(df, start_date)

    # Display the results
    print("Week 1 Summary:")
    print(week1_df.head())
    print("Week 2 Summary:")
    print(week2_df.head())


if __name__ == "__main__":
    main()
