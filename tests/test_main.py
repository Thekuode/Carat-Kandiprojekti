# This test focuses on the main function of the play_store_fetcher script
# It uses mocks to simulate:
# 
# 1. Reading package names from a CSV file
# 2. Sending a request to the Google Play Store
# 3. Extracting app information using the get_app_info_from_html function
# 4. Saving the collected data to cache and a CSV file
#
# The test makes sure that:
# 1. The correct app information is passed to the save_to_cache_and_csv function
# 2. The correct URL is requested from the Google Play Store
# 3. The package names are read from the specified CSV file



from unittest.mock import mock_open, patch
from play_store_fetcher2 import CACHE_FILE, OUTPUT_CSV_FILE

@patch("builtins.open", mock_open())
@patch("play_store_fetcher2.read_package_names", return_value=["com.example.app"])
@patch("play_store_fetcher2.send_request", return_value=type("Response", (object,), {"status_code": 200, "text": "mock"}))
@patch("play_store_fetcher2.get_app_info_from_html", return_value=("4.5", "100K+", "1M+", "Last Updated: Jan 1, 2025"))
@patch("play_store_fetcher2.save_to_cache_and_csv")
def test_main(mock_save, mock_get_info, mock_request, mock_read):
    # mock the dynamic file path or file-reading logic
    mock_read.return_value = ["com.example.app"]

    from play_store_fetcher2 import main
    main()

    # check the save_to_cache_and_csv call
    mock_save.assert_called_with("com.example.app", "4.5", "100K+", "1M+", "Last Updated: Jan 1, 2025")

    # check the request URL
    mock_request.assert_called_once_with("https://play.google.com/store/apps/details?id=com.example.app")

    # ensure package name is read
    mock_read.assert_called_once_with("./carat-data-top1k-users-2014-to-2018-08-25/allapps-with-categories-2018-12-15.csv")

