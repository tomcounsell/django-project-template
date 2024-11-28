from unittest import TestCase
from unittest.mock import patch, MagicMock
from apps.insights.services.csv_processor import CSVProcessor
import pandas as pd


class TestCSVProcessor(TestCase):
    @patch("apps.insights.services.csv_processor.load_csv")
    @patch("apps.insights.services.csv_processor.validate_columns")
    @patch("apps.insights.services.csv_processor.clean_data")
    @patch("apps.insights.services.csv_processor.filter_data")
    def test_csv_processor_workflow(
        self, mock_filter_data, mock_clean_data, mock_validate_columns, mock_load_csv
    ):
        # Mock data
        mock_data = pd.DataFrame(
            {
                "date": ["2024-01-01", "2024-01-02"],
                "traffic_source": ["organic", "paid"],
                "value": [100, 200],
            }
        )
        mock_cleaned_data = mock_data.copy()  # Assume cleaning doesn't alter much
        mock_filtered_data = mock_data[mock_data["traffic_source"] == "organic"]

        # Mock behavior
        mock_load_csv.return_value = mock_data
        mock_clean_data.return_value = mock_cleaned_data
        mock_filter_data.return_value = mock_filtered_data

        # Create an instance of CSVProcessor
        processor = CSVProcessor()

        # Test load
        processor.load()
        mock_load_csv.assert_called_once()
        self.assertIsNotNone(processor.df)
        self.assertTrue(processor.df.equals(mock_data))

        # Test validate
        processor.validate()
        mock_validate_columns.assert_called_once_with(mock_data)

        # Test clean
        processor.clean()
        mock_clean_data.assert_called_once_with(mock_data)
        self.assertTrue(processor.df.equals(mock_cleaned_data))

        # Test filter
        filtered_df = processor.filter(
            start_date="2024-01-01", traffic_source="organic"
        )
        mock_filter_data.assert_called_once_with(
            mock_cleaned_data, "2024-01-01", "organic"
        )
        self.assertTrue(filtered_df.equals(mock_filtered_data))

    @patch("apps.insights.services.csv_processor.generate_overview")
    def test_generate_overview(self, mock_generate_overview):
        # Mock data
        mock_data = pd.DataFrame(
            {
                "value": [100, 200, 300],
            }
        )

        # Create an instance of CSVProcessor
        processor = CSVProcessor()

        # Call generate_overview
        processor.generate_overview(mock_data, "Test Label")
        mock_generate_overview.assert_called_once_with(mock_data, "Test Label")
