# This test focuses on the save_to_cache_and_csv function
# It uses mocks to simulate file operations and check if the correct data is written to the correct files
#
# The test makes sure that:
# 1. The correct data is written to the cache file in the correct format
# 2. The correct data is written to the CSV file in the correct format
#
# The test simulates saving mock app information to both the cache and CSV files


import unittest
import pytest
from unittest.mock import mock_open, patch
from play_store_fetcher import CACHE_FILE, OUTPUT_FOUND_CSV_FILE, OUTPUT_ERROR_CSV_FILE, OUTPUT_MISSING_CSV_FILE, append_to_csv


MOCK_DATA = {
    "pkg": "com.example.app",
    "region": "US",
    "http_status":404,
    "url": "https:\\mock.com",
    "rating": "4.5",
    "reviews": "100K+",
    "downloads": "1M+",
    "last_updated": "Jan 1, 2025",
    "exp_msg": "Mock exception"
}

@pytest.mark.parametrize("target_csv, test_data", [
        (OUTPUT_FOUND_CSV_FILE, [MOCK_DATA["pkg"], MOCK_DATA["region"], MOCK_DATA["rating"], MOCK_DATA["reviews"], MOCK_DATA["downloads"], MOCK_DATA["last_updated"]]),
        (OUTPUT_ERROR_CSV_FILE, [MOCK_DATA["pkg"], MOCK_DATA["region"], MOCK_DATA["http_status"], MOCK_DATA["url"], MOCK_DATA["exp_msg"]]),
        (OUTPUT_MISSING_CSV_FILE, [MOCK_DATA["pkg"], MOCK_DATA["region"], MOCK_DATA["http_status"], MOCK_DATA["url"]]),
        (CACHE_FILE, [MOCK_DATA["pkg"], MOCK_DATA["region"]])
    ]            
)
@patch("builtins.open", new_callable=mock_open())
@patch("csv.writer")
def test_save_to_cache_and_csv(mock_csv_writer, mock_open, target_csv, test_data) -> None:
    mock_writer_instance = mock_csv_writer.return_value
    mock_writer_instance.writerow = unittest.mock.MagicMock()
    append_to_csv(target_csv, test_data)
    mock_open.assert_called_with(target_csv, mode='a', newline='', encoding='utf-8')
    mock_csv_writer.assert_called_with(mock_open().__enter__(), delimiter=";")
    mock_writer_instance.writerow.assert_called_with(test_data)    





