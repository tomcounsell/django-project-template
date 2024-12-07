import pandas as pd


def validate_dataframe(df: pd.DataFrame) -> None:
    """
    Validates that the input is a pandas DataFrame.

    Args:
        df (pd.DataFrame): The object to validate.

    Raises:
        TypeError: If the input is not a pandas DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected a pandas DataFrame, but got: {type(df).__name__}")
