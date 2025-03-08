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

#Test inputs as tuple[str, str, str, str]
@pytest.mark.parametrize("raw_html, expected_rating, expected_reviews, expected_downloads", 
    [
        ("Rating: 4.5 stars, 100K+ reviews, 1M+ Downloads", "4.5", "100K+", "1M+"), #When all information is present
        ("Rating: Not found, reviews: Not found, Downloads: Not found", "Not found", "Not found", "Not found"), #When all information is missing
        ("Rating: , reviews, Downloads", "Not found", "Not found", "Not found"), #When some data is missing or not found
        ("", "Not found", "Not found", "Not found"), #When the input text is empty
        ("rating: 5.0 star, 1 reviews, 1 Downloads", "5.0", "1", "1"), #When edge cases are encountered (e.g., single values)
        ("RATING: 3.3 STAR, 999 REVIEWS, 999 DOWNLOADS", "3.3", "999", "999"), #When the input text uses different capitalizations
    ]
)
def test_extract_app_info(raw_html: str, expected_rating: str, expected_reviews: str, expected_downloads: str) -> None:
    """
        Limit tests `extract_app_info()` with various inputs.

        Ensures that that the `extract_app_info()` is able to handle correctly various inputs.

        Args:
            raw_html (str): html containing the data.
            expected_rating (str): Expected rating output from the `extract_app_info()` function.
            expected_reviews (str): Expected reviews count output from the `extract_app_info()` function.
            expected_downloads (str): Expected downloads count output from the `extract_app_info()` function.
    """
    rating, reviews, downloads = extract_app_info(raw_html)
    assert rating == expected_rating
    assert reviews == expected_reviews
    assert downloads == expected_downloads