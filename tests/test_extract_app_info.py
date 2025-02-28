# These tests focus on the extract_app_info function.
# The function covers various scenarios such as:
# 
# 1. When all information is present
# 2. When all information is missing
# 3. When some data is missing or not found
# 4. When the input text is empty
# 5. When edge cases are encountered (e.g., single values)
# 6. When the input text uses different capitalizations
#
# The tests use mock text to simulate the format of the data extracted from Google Play Store pages.
# The expected output for each test is compared with the actual output returned 
# by the function and if they match, the test is considered successful.


import pytest
from play_store_fetcher2 import extract_app_info

def test_extract_app_info():
    text = "Rating: 4.5 stars, 100K+ reviews, 1M+ Downloads"
    rating, reviews, downloads = extract_app_info(text)
    assert rating == "4.5"
    assert reviews == "100K+"
    assert downloads == "1M+"

    # test with not found data
    text = "Rating: Not found, reviews: Not found, Downloads: Not found"
    rating, reviews, downloads = extract_app_info(text)
    assert rating == "Not found"
    assert reviews == "Not found"
    assert downloads == "Not found"

    # test with missing data
    text = "Rating: , reviews, Downloads"
    rating, reviews, downloads = extract_app_info(text)
    assert rating == "Not found"
    assert reviews == "Not found"
    assert downloads == "Not found"

    # test with missing information
    text = ""
    rating, reviews, downloads = extract_app_info(text)
    assert rating == "Not found"
    assert reviews == "Not found"
    assert downloads == "Not found"

    # test with edge cases
    text = "rating: 5.0 star, 1 reviews, 1 Downloads"
    rating, reviews, downloads = extract_app_info(text)
    assert rating == "5.0"
    assert reviews == "1"
    assert downloads == "1"

    # test with lowercase and uppercase characters
    text = "RATING: 3.3 STAR, 999 REVIEWS, 999 DOWNLOADS"
    rating, reviews, downloads = extract_app_info(text)
    assert rating == "3.3"
    assert reviews == "999"
    assert downloads == "999"