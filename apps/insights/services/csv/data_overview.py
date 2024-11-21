# apps/insights/services/data_overview.py


def generate_overview(df, label):
    # Generate and print statistical overview for the given DataFrame
    print(f"\nStatistical Overview - {label}:")
    print(df.describe())
