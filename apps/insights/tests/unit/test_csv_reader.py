# tests/unit/test_csv_reader.py
import pandas as pd
import pytest
from apps.insights.services.csv.csv_reader import load_csv

# Mock CSV file content
VALID_CSV_CONTENT = "col1,col2\n1,2\n3,4\n"
INVALID_CSV_CONTENT = "invalid_csv_content"


@pytest.fixture
def tmp_csv_file(tmp_path):
    """Fixture to create a temporary valid CSV file."""
    file_path = tmp_path / "valid.csv"
    file_path.write_text(VALID_CSV_CONTENT)
    return file_path


@pytest.fixture
def tmp_invalid_csv_file(tmp_path):
    """Fixture to create a temporary invalid CSV file."""
    file_path = tmp_path / "invalid.csv"
    file_path.write_text(INVALID_CSV_CONTENT)
    return file_path


def test_load_csv_valid_file(tmp_csv_file):
    """Test successful CSV loading."""
    df = load_csv(file_path=str(tmp_csv_file))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2  # Ensure rows are loaded
    assert list(df.columns) == ["col1", "col2"]


def test_load_csv_missing_file():
    """Test FileNotFoundError for a missing file."""
    with pytest.raises(FileNotFoundError):
        load_csv(file_path="missing.csv")


def test_load_csv_invalid_format(tmp_invalid_csv_file):
    """Test ValueError for malformed CSV content."""
    with pytest.raises(ValueError):
        load_csv(file_path=str(tmp_invalid_csv_file))
