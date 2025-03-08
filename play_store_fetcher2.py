import random
from typing import Union
import time
import requests
from bs4 import BeautifulSoup
import re
import os
import csv

URL_BEGIN = "https://play.google.com/store/apps/details?id="
CACHE_FILE = "cached_files.txt"
CSV_FILE_PATH = "./carat-data-top1k-users-2014-to-2018-08-25/allapps-with-categories-2018-12-15.csv"
OUTPUT_CSV_FILE = "app_data.csv"

def read_cached_packages(cache_file: str) -> set[str]:
    """
    Reads the package names that have cached data. Done to avoid redundant requests
    
    Args:
        cache_file (str): The file path of the cache file.

    Returns:
        set[str]: Package names that have existing cached data
    """
    if not os.path.exists(cache_file):
        return set()
    with open(cache_file, "r", encoding="utf-8") as f:
        return set(line.strip().split(";")[0] for line in f if line.strip())

def read_package_names(file_path: str) -> list[str]:
    """
    Reads package names from the given file and returns them as a list.

    Args:
        file_path (str): The file path of the CSV containing the package names.

    Returns:
        list[str]: A list of package names found in the CSV.
    """
    package_names = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(";")
            if parts:
                package_names.append(parts[0])  # we get only the package name and not the type
    return package_names

def send_request(url: str) -> Union[requests.Response, None]:
    """
    Makes a Get request to the given url. 

    This function sends a GET request to the specified URL and returns the response 
    object if the status code is 200. If the status code is not 200, it returns None.

    Args:
        url (str): Target for the get request.

    Returns:
        union[requests.Response, None]: The response object if the request 
        returns a status code of 200, or None if the request fails or returns 
        any other status code.
    """
    print(f"requesting {url}")
    response = requests.get(url)

    if response.status_code == 200:
        return response
    elif response.status_code == 404:
        print(f"Error 404: Page not found for {url}")
        return None
    else:
        print(f"Failed with status {response.status_code}")
        return None

def extract_app_info(raw_html: str) -> tuple[str,str,str]:
    """
    Extracts data points from the given HTML using regular expressions.

    Helper function, see `get_app_info_from_html()`. 
    This function uses regular expressions to extract the following data points:
    - Ratings: The number of stars.
    - Review count: The number of reviews left.
    - Download count: The number of times the app was downloaded.   
    If data point is not present in the html, 'Not found' is returned for it.

    Args:
        raw_html (str): The HTML content containing the extractable data.

    Returns:
        tuple[str, str, str]: A tuple containing the rating, review count, and download count as strings in that order.
        If any of the data points are not found, they are represented by the string 'Not Found'.
    """
    raw_html = raw_html.replace(",", ".")
    rating_match = re.search(r'(\d+(\.\d+)?)\s*star', raw_html, re.IGNORECASE)
    reviews_match = re.search(r'(\d+[A-Za-z\+]*?)\s*review', raw_html, re.IGNORECASE)
    downloads_match = re.search(r'(\d+[A-Za-z\+]*?)\s*download', raw_html, re.IGNORECASE)

    rating = rating_match.group(1) if rating_match else "Not found"
    reviews = reviews_match.group(1) if reviews_match else "Not found"
    downloads = downloads_match.group(1) if downloads_match else "Not found"

    return rating, reviews, downloads

def get_app_info_from_html(pkg: str, raw_html: str) -> tuple[str, str, str, str]:
    """
    Extracts data points from the given HTML.

    Parses html using BeautifulSoup. 
    If present in html, using helper function (see `extract_app_info()`) extracts following data points:
    - Ratings: The number of stars.
    - Review count: The number of reviews left.
    - Download count: The number of times the app was downloaded.   
    If present in the html, extracts the following data points:
    - Last update time: When was the last update released for the app.   
    If data point is not present in the html, 'Not found' is returned for it.
    
    Args:
        pkg (str): Package name
        raw_html (str): HTML containing the data points

    Returns:
        tuple [str, str, str, str]: A tuple containing the rating, review count, download count and last update time as strings in that order.
        If any of the data points are not found, they are represented by the string 'Not Found'.
    """
    soup = BeautifulSoup(raw_html, 'html.parser')

    # extract rating, reviews and downloads
    raw_info = soup.find("div", class_="l8YSdd")
    if raw_info:
        rating, reviews, downloads = extract_app_info(raw_info.text.strip())
    else:
        print(f"Info not found for {pkg}.")
        rating, reviews, downloads = "Not found", "Not found", "Not found"

    # extract time of last update
    last_updated_info = soup.find("div", class_="xg1aie")
    if last_updated_info:
        last_updated_time = last_updated_info.text.strip()
    else:
        print(f"Update info not found for {pkg}.")
        last_updated_time = "Not found"

    return rating, reviews, downloads, last_updated_time

def save_to_cache_and_csv(pkg: str, rating: str, reviews: str, downloads: str, last_updated: str, cache_file: str, output_file: str) -> None:
    """
    Caches and outputs the given data for the given package.

    Cache data is stored as a generic file. Each line represents a unique package, data is ';' seperated in the file.   
    Output is stored as a csv file. Data is ',' seperated.

    Args:
        pkg (str): Package name.
        rating (str): Number of stars.
        reviews (str): Number of reviews.
        downloads (str): Number of downloads.
        last_updated (str): Time of the last update.
        cache_file (str): File path to the cache file.
        output_file (str): File path to the output csv file.
    """
    # save first to cache file
    with open(cache_file, "a", encoding="utf-8") as file:
        file.write(f"{pkg};{rating};{reviews};{downloads};{last_updated}\n")

    # save to CSV file
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([pkg, rating, reviews, downloads, last_updated])

def main():
    """
    Fetches google playstore data for given packages. Outputs the data as csv.

    Reads package names from given csv file. Fetches data from google playstore for each package.
    Caches and outputs the data for each package.
    """

    package_names = read_package_names(CSV_FILE_PATH)
    cached_packages = read_cached_packages(CACHE_FILE)

    # create CSV header if the file is empty
    if not os.path.exists(OUTPUT_CSV_FILE):
        with open(OUTPUT_CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Package Name', 'Rating', 'Reviews', 'Downloads', 'Last Updated'])

    for pkg_name in package_names:
        if pkg_name in cached_packages:
            print(f"Skipping {pkg_name}, already collected")
            continue

        url = URL_BEGIN + pkg_name
        r = send_request(url)

        # if the request was successful
        if r:
            rating, reviews, downloads, last_updated = get_app_info_from_html(pkg_name, r.text)
            save_to_cache_and_csv(pkg_name, rating, reviews, downloads, last_updated, CACHE_FILE, OUTPUT_CSV_FILE)
        else:
            print(f"Skipping {pkg_name} due to a failed request")

        # use a random delay between 2 and 4 seconds to avoid getting blocked
        delay = random.uniform(2, 4)
        time.sleep(delay)

if __name__ == "__main__":
    main()

























