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
OUTPUT_HTML_FOLDER = "raw_html_output"

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

def save_pkg_data(pkg: str, rating: str, reviews: str, downloads: str, last_updated: str, raw_html: str, cache_file: str, output_file: str, output_html_folder: str) -> None:
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
        raw_html (str): The raw html for the package get.
        cache_file (str): File path to the cache file.
        output_file (str): File path to the output csv file.
        output_html_folder (str): output path for the raw html.
    """
    # save first to cache file
    with open(cache_file, "a", encoding="utf-8") as file:
        file.write(f"{pkg};{rating};{reviews};{downloads};{last_updated}\n")

    # save to CSV file
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([pkg, rating, reviews, downloads, last_updated])

    # save raw html for the package
    raw_html_output_path = f"{output_html_folder}/{pkg}_raw_html.html"
    with open(raw_html_output_path, "w", encoding="utf-8") as file:
        file.write(raw_html)

def init_checks(package_input_csv: str, output_csv_file: str, output_html_folder: str) -> tuple[bool, str]:
    """
    Checks and creates all expected folders and files.

    Checks the following things:
        - Does the given csv input file exists? Returns error if not
        - Does the output csv exists? if not creates it.
        - Does the raw html folder exists? if not creates it.

    Args:
        package_input_csv (str): file path to the input csv file, containing the package names.
        output_csv_file (str): output csv file path.
        output_html_folder (str): output path for the package html files

    Returns:
        tuple[bool,str]: Were all the checks and initializations succesful and a potential error message.
    """
    #Check that the package name csv input file exists
    if not os.path.exists(package_input_csv):
        return (False, "Could not read input package file!")
    
    #Check if the ouput csv file exists, if not create it
    if not os.path.exists(output_csv_file):
        # create CSV header if the file is empty
        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Package Name', 'Rating', 'Reviews', 'Downloads', 'Last Updated'])

    #Check that html output folder exists
    if not os.path.exists(output_html_folder):
        os.mkdir(output_html_folder)
    
    #All good
    return (True, "")
    


def main() -> None:
    """
    Fetches google playstore data for given packages. Outputs the data as csv.

    Reads package names from given csv file. Fetches data from google playstore for each package.
    Caches and outputs the data for each package.
    """

    #Check and create all folders and files for operation
    init_successful, init_error_msg = init_checks(CSV_FILE_PATH, OUTPUT_CSV_FILE, OUTPUT_HTML_FOLDER)
    if init_successful:
        #Read package names and cache contents
        package_names = read_package_names(CSV_FILE_PATH)
        cached_packages = read_cached_packages(CACHE_FILE)

        #Request google playstore pages
        for pkg_name in package_names:
            if pkg_name in cached_packages:
                print(f"Skipping {pkg_name}, already collected")
                continue

            url = URL_BEGIN + pkg_name
            r = send_request(url)

            # if the request was successful
            if r:
                rating, reviews, downloads, last_updated = get_app_info_from_html(r.text)
                save_pkg_data(pkg_name, rating, reviews, downloads, last_updated, r.text, CACHE_FILE, OUTPUT_CSV_FILE, OUTPUT_HTML_FOLDER)
            else:
                print(f"Skipping {pkg_name} due to a failed request")

            # use a random delay between 2 and 4 seconds to avoid getting blocked
            delay = random.uniform(2, 4)
            time.sleep(delay)
    else:
        #Something went wrong, error msg before exit
        print(init_error_msg)

if __name__ == "__main__":
    main()

























