import json
import numpy as np
import pandas as pd

OUTPUT_FILE = "overview_2024-01-01.json"


def generate_overview(df: pd.DataFrame) -> str:
    """
    Generates a statistical overview for the given DataFrame and optionally saves it as a JSON file.

    Args:
        df (DataFrame): The DataFrame to generate an overview for.

    Returns:
        str: Statistical overview as a string.
    """
    # Drop date field before generating the statistical overview
    if "date" in df.columns:
        df = df.drop(columns=["date"])

    # Generate the statistical overview as a string
    statistical_overview = df.describe().to_string()
    print(statistical_overview)

    # TEMPORARY: Save structured overview to JSON
    if OUTPUT_FILE:
        # Convert to dictionary and handle NaN values
        overview_dict = df.describe().to_dict()
        for col, metrics in overview_dict.items():
            for key, value in metrics.items():
                if isinstance(value, (pd.Timestamp, np.datetime64)):
                    overview_dict[col][
                        key
                    ] = value.isoformat()  # Convert Timestamps to ISO
                elif pd.isna(value):  # Handle NaN
                    overview_dict[col][key] = None

        # Save as JSON
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(overview_dict, f, indent=4, ensure_ascii=False)
        print(f"Overview saved to {OUTPUT_FILE}")

    return statistical_overview
