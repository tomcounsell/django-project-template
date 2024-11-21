from insights.services.csv_reader import load_csv, validate_columns


def main():
    # Path to the CSV file
    file_path = "insights/data/ga4_data.csv"

    # Step 1: Load CSV
    print("Loading CSV...")
    df = load_csv(file_path)

    # Step 2: Validate columns
    print("Validating columns...")
    validate_columns(df)

    # Step 3: Preview DataFrame (no cleaning yet)
    print("CSV loaded successfully:")
    print(df.head())


if __name__ == "__main__":
    main()
