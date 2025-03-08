# This test focuses on the save_to_cache_and_csv function
# It uses mocks to simulate file operations and check if the correct data is written to the correct files
#
# The test makes sure that:
# 1. The correct data is written to the cache file in the correct format
# 2. The correct data is written to the CSV file in the correct format
#
# The test simulates saving mock app information to both the cache and CSV files



from unittest.mock import mock_open, patch
from play_store_fetcher import CACHE_FILE, OUTPUT_CSV_FILE, save_to_cache_and_csv

@patch("builtins.open", mock_open())
def test_save_to_cache_and_csv() -> None:
    mock_pkg = "com.example.app"
    mock_rating = "4.5"
    mock_reviews = "100K+"
    mock_downloads = "1M+"
    mock_last_updated = "Jan 1, 2025"

    # mock file opening and writing
    save_to_cache_and_csv(mock_pkg, mock_rating, mock_reviews, mock_downloads, mock_last_updated, CACHE_FILE, OUTPUT_CSV_FILE)

    # make sure that write operations happen for the cache file
    with open(CACHE_FILE, "a", encoding="utf-8") as file:
        file.write.assert_any_call(f"{mock_pkg};{mock_rating};{mock_reviews};{mock_downloads};{mock_last_updated}\n")

    # make sure that write operations happen for the CSV file
    with open(OUTPUT_CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        file.write.assert_any_call(f"{mock_pkg},{mock_rating},{mock_reviews},{mock_downloads},\"{mock_last_updated}\"\r\n")




