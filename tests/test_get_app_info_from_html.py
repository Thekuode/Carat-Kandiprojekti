# These tests focus on the get_app_info_from_html function
# The function and cover various scenarios such as:
# 
# 1. When all information is present
# 2. When some information is missing 
# 3. When all information is missing
# 4. When the HTML is not in a correct format
# 5. When only parts of the information are available
#
# The tests use mock HTML to simulate the structure of real Google Play Store pages.
# The expected output for each test is compared with the actual output returned 
# by the function and if they match, the test is considered successful

import pytest
from play_store_fetcher2 import get_app_info_from_html

def test_get_app_info_from_html():
    # test when all the requested information is present
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">Rating: 4.5 stars, 100K+ reviews, 1M+ Downloads</div>
            <div class="xg1aie">Last Updated: Jan 1, 2025</div>
        </body>
    </html>
    '''
    expected = ("4.5", "100K+", "1M+", "Last Updated: Jan 1, 2025")
    result = get_app_info_from_html("com.example.app", mock_html)
    assert result == expected

def test_get_app_info_from_html_missing_info():
    # test when last updated info is missing
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">Rating: 4.5 stars, 100K+ reviews, 1M+ Downloads</div>
        </body>
    </html>
    '''
    expected = ("4.5", "100K+", "1M+", "Not found")
    result = get_app_info_from_html("com.example.app", mock_html)
    assert result == expected

def test_get_app_info_from_html_no_info():
    # test when all info is missing
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">No relevant info</div>
        </body>
    </html>
    '''
    expected = ("Not found", "Not found", "Not found", "Not found")
    result = get_app_info_from_html("com.example.app", mock_html)
    assert result == expected

def test_get_app_info_from_html_incomplete_info():
    # test when rating info is missing
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">100K+ reviews, 1M+ Downloads</div>
            <div class="xg1aie">Last Updated: Jan 1, 2025</div>
        </body>
    </html>
    '''
    expected = ("Not found", "100K+", "1M+", "Last Updated: Jan 1, 2025")
    result = get_app_info_from_html("com.example.app", mock_html)
    assert result == expected

def test_get_app_info_from_html_invalid_format():
    # test when the HTML format is invalid or unexpected
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">Invalid format</div>
        </body>
    </html>
    '''
    expected = ("Not found", "Not found", "Not found", "Not found")
    result = get_app_info_from_html("com.example.app", mock_html)
    assert result == expected

def test_get_app_info_from_html_rating_only():
    # test when only rating is provided in the HTML
    mock_html = '''
    <html>
        <body>
            <div class="l8YSdd">Rating: 4.5 stars</div>
        </body>
    </html>
    '''
    expected = ("4.5", "Not found", "Not found", "Not found")
    result = get_app_info_from_html("com.example.app", mock_html)
    assert result == expected
















