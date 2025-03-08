# This test focuses on the read_package_names function
# It uses a fixture to create a temporary CSV file with mock data for testing
#
# The test makes sure that:
# 1. The package names are correctly extracted from the CSV file
# 2. The function handles various formats
#
# The expected output is a list of package names without the category or any other additional data



import pytest
from play_store_fetcher import read_package_names

# example input and expected output
@pytest.fixture
def sample_csv_file(tmp_path) -> str:
    # create a temporary file for testing purposes
    csv_file = tmp_path / "test.csv"
    content = "com.example.app1;category1\ncom.example.app2;category2\naa.aaaa.aaa;aaa\ncom.example.app3;____\na.a.a"
    csv_file.write_text(content)
    return csv_file

def test_read_package_names(sample_csv_file) -> None:
    packages = read_package_names(str(sample_csv_file))
    assert packages == ["com.example.app1", 
                        "com.example.app2", 
                        "aa.aaaa.aaa", 
                        "com.example.app3", 
                        "a.a.a"]