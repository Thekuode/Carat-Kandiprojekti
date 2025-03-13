import random
from typing import Union
from collections import defaultdict
import time
import requests
from bs4 import BeautifulSoup
import re
import os
import csv

CACHE_FILE = "cached_files.txt"
CSV_FILE_PATH = "./carat-data-top1k-users-2014-to-2018-08-25/allapps-with-categories-2018-12-15.csv"
OUTPUT_CSV_FILE = "app_data.csv"
OUTPUT_HTML_FOLDER = "raw_html_output"

def get_app_info_from_html(raw_html: str) -> tuple[str, str, str, str]:
    """
    Extracts data points from the given HTML.

    Parses html using BeautifulSoup. 
    If present in the html, extracts the following data points:
    - Ratings: The number of stars.
    - Review count: The number of reviews left.
    - Download count: The number of times the app was downloaded.
    - Last update time: When was the last update released for the app.   
    If data point is not present in the html, 'Not found' is returned for it.
    
    Args:
        raw_html (str): HTML containing the data points

    Returns:
        tuple[str, str, str, str]: A tuple containing the rating, review count, download count and last update time as strings in that order.
        If any of the data points are not found, they are represented by the string 'Not Found'.
    """
    soup = BeautifulSoup(raw_html, 'html.parser')

    #CSS selector paths for data
    scrape_css_paths = {
        "star_rating": "div.l8YSdd div.w7Iutd div.wVqUob div.ClM7O div div.TT9eCd",
        "download_count": "div.l8YSdd div.w7Iutd div:nth-last-of-type(2) div.ClM7O", #Select 2nd last always. Rating data not always available.
        "review_count": "div.l8YSdd div.w7Iutd div.wVqUob div.g1rdde", #If rating data is not available, will match to download. Filter handles it.
        "last_updated_time": "section.HcyOxe div.SfzRHd div.TKjAsc div div.xg1aie"
    }

    #Matches floats, ints, quantity data with postfix K,M or B, datetimes
    filter_regex = r'(\d+\.\d+(K|M|B)\+?|\d+(K|M|B)\+?|\d+\.\d+|\d+\b|\b[A-Za-z]{3} \d{1,2}, \d{4}\b)'
    scaped_data = {k:"Not Found" for k,p in scrape_css_paths.items()}
    #Try to find data for each defined css path
    for data_key, css_path in scrape_css_paths.items():
         html_element = soup.select_one(css_path)
         if html_element:
            #Filter all the non wanted elements
            filtered_regex = re.findall(filter_regex, html_element.get_text(strip=True))
            filtered_value =  ' '.join([fv[0] for fv in filtered_regex])
            if filtered_value:
                scaped_data[data_key] = filtered_value

    #This expects that we use python +3.7, dict order needs to be guaranteed
    return tuple(scaped_data.values())

def save_pkg_data(pkg: str, data_region: str, http_status: int, rating: str, reviews: str, downloads: str, last_updated: str, raw_html: str, output_file: str, output_html_folder: str) -> None:
    """
    Saves the package data, including metadata and raw HTML, to specified output files.

    This function stores the following information:
    - Fetched data (name, region, http_status, rating, review, download_count, last_update_time) for package into the output csv file.
    - Raw html into the html file into the html output folder. Name is formed by combining f'{pkgname}_{region}.html'.

    Args:
        pkg (str): The name of the package.
        data_region (str): The region from which the package data was fetched.
        http_status (int): The HTTP status of the data request.
        rating (str): The package's rating (in stars).
        reviews (str): The number of reviews for the package.
        downloads (str): The number of downloads for the package.
        last_updated (str): The last update timestamp for the package.
        raw_html (str): The raw HTML content for the package.
        output_file (str): The file path for the output CSV file.
        output_html_folder (str): The folder path to store the raw HTML files.

    Returns:
        None
    """
    # save to CSV file
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([pkg, data_region, http_status, rating, reviews, downloads, last_updated])

    # save raw html for the package
    raw_html_output_path = f"{output_html_folder}/{pkg}_{data_region}.html"
    with open(raw_html_output_path, "w", encoding="utf-8") as file:
        file.write(raw_html)

def form_playstore_url(pkg: str, language:str, region: str) -> str:
    """
    Given playstore package, language and region, forms and returns a valid playstore url.

    Args:
        pkg (str): Targeted package page.
        language (str): Targeted language (Optional). Empty or ISO 639-1 language code.
        region (str): Targeted region (Optional). Empty or ISO 3166-1 alpha-2 country code.

    Returns:
        str: Valid google playstore url for the targeted parameters.
    """
    base_url = "https://play.google.com/store/apps/details?id="
    playstore_url = f"{base_url}{pkg}"
    if region:
        playstore_url = f"{playstore_url}&gl={region}"
    if language:
        playstore_url = f"{playstore_url}&hl={language}"
    return playstore_url

def read_cached_packages(cache_file: str) -> set[str]:
    """
    Reads the package names from the cache file that have cached data to avoid redundant requests.

    This function parses the cache file to extract the package names that already have cached data.
    Args:
        cache_file (str): The file path to the cache file storing package names and their regions.

    Returns:
        set[str]: A set of package names that have existing cached data.
    """
    package_cache = defaultdict(list)
    if os.path.exists(cache_file):
        with open(cache_file, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            #pkg;region
            for line in csv_reader:
                package_cache[line[0]].append(line[1])
    return package_cache
    
def add_package_to_cache(cache_file: str, cache: dict[list[str]], pkg: str, data_region:str) -> None:
    """
    Adds the package and its fetched region to the cache and appends it to the cache file.

    This function updates the cache dictionary by appending the region to the list of cached regions for 
    the given package. It also appends the package and region to the specified cache file.

    Args:
        cache_file (str): The location of the cache file where the package and region are stored.
        cache (dict[list[str]]): A dictionary where package names are keys, and values are lists of regions.
        pkg (str): The name of the package to add to the cache.
        data_region (str): The region from which the data for the package was fetched.

    Returns:
        None
    """
    cache[pkg].append(data_region)
    with open(cache_file, "a", encoding="utf-8") as file:
        file.write(f"{pkg};{data_region}\n")

def package_is_cached(cache: dict[list[str]],package: str, data_region: str) -> bool:
    """
    Checks if the package is cached for the specified region.

    This function checks if the given package has cached data for the specified region.

    Args:
        cache (dict[list[str]]): A dictionary where keys are package names, and values are lists of regions where data is cached.
        package (str): The name of the package to check.
        data_region (str): The region (ISO 3166-1 alpha-2 country code) to check for the package.
    Returns:
        bool: True if the package is cached for the specified region, False otherwise.
    """
    return package in cache.keys() and data_region in cache[package]

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

def fetch_playstore_data_from_regions(cache_file: str, cached_packages: dict[list[str]], package: str, regions: list[str]) -> None:
    """
    Fetches Play Store data for a given package in each specified region.

    This function interacts with the package cache to fetch Play Store data for the specified package. 
    It retrieves data for missing regions and updates both the cache and the cache file.

    Args:
        cache_file (str): Path to the cache file where package data is stored.
        cached_packages (dict[list[str]]): A dictionary mapping package names to lists of regions where data has been fetched.
        package (str): The name of the package to fetch data for.
        regions (list[str]): A list of ISO 3166-1 alpha-2 country codes representing the regions to fetch data for.
    Returns:
        None
    """
    for region in regions:
        print(f"Collecting {package}/{region}: ", end="")
        #Already fetched?
        if package_is_cached(cached_packages, package, region):
            print("Is cached, skipping")
            continue

        playstore_url = form_playstore_url(package, "en", region)
        playstore_response = requests.get(playstore_url)

        # if the request was successful
        if playstore_response.status_code == 200 or playstore_response.status_code == 404:
            print(f"Request sucess ({playstore_response.status_code}), saving data")
            rating, reviews, downloads, last_updated = get_app_info_from_html(playstore_response.text)
            save_pkg_data(package, region, playstore_response.status_code, rating, reviews, downloads, last_updated, playstore_response.text, OUTPUT_CSV_FILE, OUTPUT_HTML_FOLDER)
            add_package_to_cache(cache_file, cached_packages, package, region)
        elif playstore_response.status_code == 429:
            #Too many request, try again in a hour
            print("Too many requests, stopping for an hour")
            time.sleep(3600)
        else:
            print("Request failed")

def init_checks(package_input_csv: str, output_csv_file: str, output_html_folder: str) -> tuple[bool, str]:
    """
    Checks and creates the expected folders and files needed for the process.

    This function performs the following checks and actions:
        - Verifies if the input CSV file exists. Returns an error message if it doesn't.
        - Checks if the output CSV file exists. If it doesn't, creates it.
        - Checks if the raw HTML folder exists. If it doesn't, creates it.

    Args:
        package_input_csv (str): Path to the input CSV file containing package names.
        output_csv_file (str): Path to the output CSV file.
        output_html_folder (str): Path to the folder for storing raw HTML files.

    Returns:
        tuple[bool, str]: A tuple where the first element is a boolean indicating whether
        all checks and initializations were successful, and the second element
        is an error message if there was any issue (empty string if successful).
    """
    #Check that the package name csv input file exists
    if not os.path.exists(package_input_csv):
        return (False, "Could not read input package file!")
    
    #Check if the ouput csv file exists, if not create it
    if not os.path.exists(output_csv_file):
        # create CSV header if the file is empty
        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Package Name', 'Data Region', 'Http Status', 'Rating', 'Reviews', 'Downloads', 'Last Updated'])

    #Check that html output folder exists
    if not os.path.exists(output_html_folder):
        os.mkdir(output_html_folder)
    
    #All good
    return (True, "")

def main() -> None:
    """
    Fetches Google Play Store data for the given packages and outputs the data as a CSV file.

    This function reads package names from the specified CSV file, fetches data from the Google Play Store 
    for each package in each defined region, and caches the results. It then outputs the fetched data to a CSV file and stores the raw html.

    Returns:
        None
    """
    #Check and create all folders and files for operation
    init_successful, init_error_msg = init_checks(CSV_FILE_PATH, OUTPUT_CSV_FILE, OUTPUT_HTML_FOLDER)
    if init_successful:
        #Read package names and cache contents
        package_names = read_package_names(CSV_FILE_PATH)
        cached_packages = read_cached_packages(CACHE_FILE)
        fetch_regions = ["US"]
        #Request google playstore pages
        for pkg_name in package_names:
            #Fetch data for the package in the regions
            fetch_playstore_data_from_regions(CACHE_FILE, cached_packages, pkg_name, fetch_regions)
            # use a random delay between 2 and 4 seconds to avoid getting blocked
            delay = random.uniform(2, 4)
            time.sleep(delay)
    else:
        #Something went wrong, error msg before exit
        print(init_error_msg)

if __name__ == "__main__":
    main()