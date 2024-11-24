# apps/insights/services/csv/data_overview.py


def generate_overview(self, df, label):
    """
    Generate a statistical overview for the given DataFrame.

    Args:
        df (DataFrame): The DataFrame to generate an overview for.
        label (str): A label for logging (e.g., Week 1 or Week 2).
    """
    logging.info(f"Generating statistical overview for {label}...")
    print(f"\nStatistical Overview - {label}:")
    print(df.describe())
