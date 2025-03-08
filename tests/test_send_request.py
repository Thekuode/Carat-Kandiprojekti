# These tests focus on the send_request function
# The tests simulate two scenarios: a successful request and a 404 error
#
# The test ensures that:
# 1. When a successful response is returned the function correctly handles it
# 2. When a 404 error response is returned the function returns None, indicating an error
#
# The tests use mock responses to simulate different status codes and ensure the function behaves as expected
# without actually making network requests.



import pytest
from unittest.mock import patch, MagicMock
from play_store_fetcher import send_request

# simulate a successful response
@pytest.fixture
def mock_successful_request() -> MagicMock:
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html></html>"
        yield mock_get

# simulate a 404 error response
@pytest.fixture
def mock_404_request() -> MagicMock:
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        yield mock_get

def test_send_request_success(mock_successful_request) -> None:
    url = "https://play.google.com/store/apps/details?id=com.example.app"
    response = send_request(url)
    assert response.status_code == 200

def test_send_request_404(mock_404_request) -> None:
    url = "https://play.google.com/store/apps/details?id=com.example.notapp"
    response = send_request(url)
    assert response is None
