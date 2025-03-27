from requests.exceptions import RequestException
from collections.abc import Iterable
from collections import defaultdict
from bs4 import BeautifulSoup
import requests
import argparse
import random
import time
import csv
import re
import os

CACHE_FILE = "cached_pkgs.csv"
OUTPUT_FOUND_CSV_FILE = "pkg_data_found.csv"
OUTPUT_MISSING_CSV_FILE = "pkg_missing.csv"
OUTPUT_ERROR_CSV_FILE = "pkg_error.csv"
OUTPUT_HTML_FOLDER = "raw_html_output"

def append_to_csv(output_path: str, data: Iterable[any]) -> None:
    """
    Appends the given data to the given csv file.

    If the given path does not exist, creates the csv file. Proceeds to append the given data to the
    given csv file.

    Args:
        output_path (str): Path to the csv file.
        data (Iterable[any]): Data to output to the csv file.
    
    Returns:
        None
    """
    with open(output_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(data)

def get_app_info_from_html(raw_html: str) -> tuple[str, str, str, str]:
    """
    Extracts data points from the given HTML.

    Parses html using BeautifulSoup. 
    If present in the html, extracts the following data points and returns them in this order:
    - Ratings: The number of stars.
    - Download count: The number of times the app was downloaded.
    - Review count: The number of reviews left.
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
    scrape_css_data = {
        "star_rating": {"css_selector" : "div.l8YSdd div.w7Iutd div.wVqUob div.ClM7O div div.TT9eCd", "filter": r"(?:[^\w\d]*)(\d+\.\d+|\d+)(?=[A-Za-z]+)", "filter_join": False},
        "download_count": {"css_selector" : "div.l8YSdd div.w7Iutd div div.ClM7O:not(:has(> img)):not(:has(> div)):not(:has(> span))", "filter": r"(\d+(\.\d+)?[KMB]?\+?)", "filter_join": False}, #Tricky to select
        "review_count": {"css_selector" : "div.l8YSdd div.w7Iutd div.wVqUob div.g1rdde", "filter": r"(\d+(\.\d+)?[KMB]?\+?)", "filter_join": False}, #If rating data is not available, will match to "downloads" text. Filter handles it.
        "last_updated_time": {"css_selector" : "div.xg1aie", "filter": r"(?:Last\sUpdated:\s)?([A-Za-z]{3})\s(\d{1,2},)\s(\d{4})", "filter_join": True},
    }

    scaped_data = {k:"Not Found" for k,p in scrape_css_data.items()}
    #Try to find data for each defined css path
    for data_key, scrape_data in scrape_css_data.items():
         html_element = soup.select_one(scrape_data["css_selector"])
         if html_element:
            #Filter all the non wanted elements
            filtered_regex = re.findall(scrape_data["filter"], html_element.get_text(strip=True))
            if filtered_regex:
                filtered_value = filtered_regex[0]
                #If filter needs to be joined
                if scrape_data["filter_join"] and not isinstance(filtered_value, str):
                    filtered_value = ' '.join([v for v in filtered_value if v])
                #If not, select 0 index
                elif not isinstance(filtered_value, str):
                    filtered_value = filtered_value[0]
                if filtered_value:
                    scaped_data[data_key] = filtered_value

    #This expects that we use python +3.7, dict order needs to be guaranteed
    return tuple(scaped_data.values())

def save_pkg_data(pkg: str, data_region: str, rating: str, reviews: str, downloads: str, last_updated: str, raw_html: str, output_prefix: str) -> None:
    """
    Saves the package data, including metadata and raw HTML, to specified output files.

    This function stores the following information:
    - Fetched data (name, region, rating, review, download_count, last_update_time) for package into the output csv file.
    - Raw html into the html file into the html output folder. Name is formed by combining f'{pkgname}_{region}.html'.
    Output file prefix contained in variable `output_prefix` is considered when outputing data to files.
    
    Args:
        pkg (str): The name of the package.
        data_region (str): The region from which the package data was fetched.
        rating (str): The package's rating (in stars).
        reviews (str): The number of reviews for the package.
        downloads (str): The number of downloads for the package.
        last_updated (str): The last update timestamp for the package.
        raw_html (str): The raw HTML content for the package.
        output_prefix (str): Output file name prefix.

    Returns:
        None
    """
    # save to CSV file
    append_to_csv(f"{output_prefix}{OUTPUT_FOUND_CSV_FILE}", [pkg, data_region, rating, reviews, downloads, last_updated])

    # save raw html for the package
    raw_html_output_path = f"{output_prefix}{OUTPUT_HTML_FOLDER}/{pkg}_{data_region}.html"
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

def read_cached_packages(output_prefix: str) -> set[str]:
    """
    Reads the package names from the cache file that have cached data to avoid redundant requests.

    This function parses the cache file to extract the package names that already have cached data.
    Output file prefix contained in `output_prefix` is considered when reading cache csv file. 

    Args:
        output_prefix (str): Output file name prefix.

    Returns:
        set[str]: A set of package names that have existing cached data.
    """
    package_cache = defaultdict(list)
    if os.path.exists(f"{output_prefix}{CACHE_FILE}"):
        with open(f"{output_prefix}{CACHE_FILE}", newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            #pkg,region
            for line in csv_reader:
                package_cache[line[0]].append(line[1])
    return package_cache
    
def add_package_to_cache(output_prefix: str, cache: defaultdict[list[str]], pkg: str, data_region:str) -> None:
    """
    Adds the package and its fetched region to the cache and appends it to the cache file.

    This function updates the cache dictionary by appending the region to the list of cached regions for 
    the given package. It also appends the package and region to the specified cache file. Prefix contained in
    `output_prefix` is considered when outputing to the cache file.

    Args:
        output_prefix (str): Prefix for the output files.
        cache (dict[list[str]]): A dictionary where package names are keys, and values are lists of regions.
        pkg (str): The name of the package to add to the cache.
        data_region (str): The region from which the data for the package was fetched.

    Returns:
        None
    """
    cache[pkg].append(data_region)
    append_to_csv(f"{output_prefix}{CACHE_FILE}", [pkg, data_region])

def package_is_cached(cache: defaultdict[list[str]], package: str, data_region: str) -> bool:
    """
    Checks if the package is cached for the specified region.

    This function checks if the given package has cached data for the specified region.

    Args:
        cache (defaultdict[list[str]]): A dictionary where keys are package names, and values are lists of regions where data is cached.
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
                package_names.append(parts[0].split(":")[0])  # we get only the package name and filter any process postfixes
    return package_names

def get_cached_html_file(output_prefix, package, region):
    html_path = f"{output_prefix}{OUTPUT_HTML_FOLDER}/{package}_{region}.html"
    if os.path.exists(html_path):
        raw_html = ""
        with open(html_path, 'r', encoding='utf-8') as file:
            raw_html = file.read()
        #Spoof a Response object
        response = requests.Response()
        response.status_code = 200
        response._content = raw_html.encode("utf-8")
        return response
    return None

def send_request(url: str) -> requests.Response:
    """
    Makes a Get request to the given url. 

    This function sends a GET request to the specified URL and returns the response 
    object

    Args:
        url (str): Target for the get request.

    Returns:
        requests.Response: The response object
    
    Raises:
        RequestException: If the request fails for any reason, throws subexception of RequestException
    """
    return requests.get(url)

def fetch_playstore_data_from_regions(output_prefix: str, cached_packages: defaultdict[list[str]], package: str, regions: list[str], use_cached_html: bool) -> None:
    """
    Fetches Play Store data for a given package in each specified region.

    This function interacts with the package cache to fetch Play Store data for the specified package. 
    It retrieves data for missing regions and updates both the cache and the cache file.

    Args:
        output_prefix (str): Prefix of the output files.
        cached_packages (dict[list[str]]): A dictionary mapping package names to lists of regions where data has been fetched.
        package (str): The name of the package to fetch data for.
        regions (list[str]): A list of ISO 3166-1 alpha-2 country codes representing the regions to fetch data for.

    Returns:
        None
    """
    for region in regions:
        print(f"Collecting {package}/{region}: ", end="")
        #Already fetched? are we rerunning data collection on cached files?
        pkg_is_cached = package_is_cached(cached_packages, package, region)
        if pkg_is_cached and not use_cached_html:
            print("Is cached, skipping")
            continue

        playstore_url = form_playstore_url(package, "en", region)
        try:
            playstore_response = None

            #We are basicly rerunning data collection on cached files
            if use_cached_html and pkg_is_cached:
                playstore_response = get_cached_html_file(output_prefix, package, region)

            #Not a rerun, or data was not available
            if not use_cached_html or (not pkg_is_cached and use_cached_html) or not playstore_response:
                #Set the sleep flag if we are here from failed cache fetch
                pkg_is_cached = False
                #Request may throw exception for various reasons
                playstore_response = send_request(playstore_url)
                
            # if the request was successful
            if playstore_response.status_code == 200 or playstore_response.status_code == 404:
                print(f"Request success ({playstore_response.status_code}) ", end="")
                if playstore_response.status_code == 200:
                    print("Saving data")
                    rating, downloads, reviews, last_updated = get_app_info_from_html(playstore_response.text)
                    save_pkg_data(package, region, rating, reviews, downloads, last_updated, playstore_response.text, output_prefix)
                else:
                    print("Data not found")
                    append_to_csv(f"{output_prefix}{OUTPUT_MISSING_CSV_FILE}", [package, region, playstore_response.status_code, playstore_url])
                #Cache the pkg for the region regardless of the HTTP status
                if not pkg_is_cached:
                    add_package_to_cache(output_prefix, cached_packages, package, region)
            else:
                print(f"Server returned error ({playstore_response.status_code})")
                if playstore_response.status_code == 429:
                    #Too many request, try again in a hour
                    print("Too many requests, stopping for an hour")
                    time.sleep(3600)
                append_to_csv(f"{output_prefix}{OUTPUT_ERROR_CSV_FILE}", [package, region, playstore_response.status_code, playstore_url, ""])
        except RequestException as e:
            print(f"Request failed: {e}")
            append_to_csv(f"{output_prefix}{OUTPUT_ERROR_CSV_FILE}", [package, region, -1, playstore_url, repr(e)])

        # use a random delay between 2 and 4 seconds to avoid getting blocked
        if not pkg_is_cached:
            delay = random.uniform(2, 4)
            time.sleep(delay)
            
def init_checks(package_input_csv: str, output_prefix: str) -> tuple[bool, str]:
    """
    Checks and creates the expected folders and files needed for the process.

    This function performs the following checks and actions:
        - Verifies if the input CSV file exists. Returns an error message if it doesn't.
        - Checks if the output CSV files exists. If it doesn't, creates it.
        - Checks if the raw HTML folder exists. If it doesn't, creates it.
    Prefix contained in `output_prefix` is considered when checking for file existence.
        
    Args:
        package_input_csv (str): Path to the input CSV file containing package names.
        output_prefix (str): Prefix for the output file names.

    Returns:
        tuple[bool, str]: A tuple where the first element is a boolean indicating whether
        all checks and initializations were successful, and the second element
        is an error message if there was any issue (empty string if successful).
    """
    #Check that the package name csv input file exists
    if not os.path.exists(package_input_csv):
        return (False, "Could not find the input package listing file!")
    
    #Check that html output folder exists. Also creates any possible prefix folders
    if not os.path.exists(f"{output_prefix}{OUTPUT_HTML_FOLDER}"):
        os.makedirs(f"{output_prefix}{OUTPUT_HTML_FOLDER}", exist_ok=True)

    output_csv_check = {
        
        f"{output_prefix}{OUTPUT_FOUND_CSV_FILE}": ['Package Name', 'Data Region', 'Rating', 'Reviews', 'Downloads', 'Last Updated'],
        f"{output_prefix}{OUTPUT_MISSING_CSV_FILE}": ['Package Name', 'Data Region', 'Http Status', 'Url'],
        f"{output_prefix}{OUTPUT_ERROR_CSV_FILE}": ['Package Name', 'Data Region', 'Http Status', 'Url', 'Exception Message'],
    }
    #Check if the ouput csv file exists, if not create it
    for path, header in output_csv_check.items():
        if not os.path.exists(path):
            # create CSV header if the file is empty
            with open(path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(header)


    
    #All good
    return (True, "")

def main(input_file: str, regions: list[str], output_prefix: str, use_cached_html: bool) -> None:
    """
    Fetches Google Play Store data for the given packages and outputs the data as a CSV file.

    This function reads package names from the specified CSV file, fetches data from the Google Play Store 
    for each package in each defined region, and caches the results. It then outputs the fetched data to a CSV file and stores the raw html.
    Output file names are prefixed with the string contained in `output_prefix`. If the use_cached_html flag is set, cached html files will be
    used instead of fetching data from playstore.

    Args:
        input_file (str): File path containing the packages to fetch
        regions (list[str]): Regions to fetch data from.
        output_prefix (str): Prefix for output files.
        use_cached_html (bool): Use cached html files.
    Returns:
        None
    """
    #Check and create all folders and files for operation
    init_successful, init_error_msg = init_checks(input_file, output_prefix)
    if init_successful:
        #Read package names and cache contents
        package_names = read_package_names(input_file)
        cached_packages = read_cached_packages(output_prefix)
        #Request google playstore pages
        for pkg_name in package_names:
            #Fetch data for the package in the regions
            fetch_playstore_data_from_regions(output_prefix, cached_packages, pkg_name, regions, use_cached_html)
    else:
        #Something went wrong, error msg before exit
        print(init_error_msg)

def parse_console_arguments() -> tuple[str,Iterable[str], str, bool]:
    """
    Parses command-line arguments for fetching data from the Google Play Store.

    This function sets up the argument parser, processes the command-line arguments,
    and returns the file path to the package listing, the regions to fetch data from,
    an optional prefix for output file names, and a flag indicating if the cached html files
    should be used instead of fetching data from playstore.

    Command-line arguments:
        --package_listing (str): The file path to the CSV file (';' delimiter expected) containing the listing of packages to fetch.
        --regions (str): A comma-separated list of regions to fetch data from (e.g., US,FI,JA).
                         Defaults to "US" if not provided.
        --output_prefix (str): An optional prefix to key the output file names, enabling separate output files/folders.
                               (e.g., "FIN" => "FIN_raw_html_output"). Defaults to an empty string if not provided.
        --use_cached_html (bool): An optional option to use the cached html files rather than fetching html files from the
                               playstore. Defaults to False.

    Returns:
        tuple: A tuple containing four elements:
            - `package_listing` (str): The file path to the package listing.
            - `regions` (list[str]): A list of regions specified by the user, or ["US"] if no regions are provided.
            - `output_prefix` (str): The optional prefix to be used in output file names, or an empty string if not provided.
            - `use_cached_html` (bool): The optional option to use cached html files rather than fetching data from playstore.

    Example usage:
        python script.py --package_listing path/to/packages.csv --regions US,FI,JA --output_prefix FIN --use_cached_html False

    Notes:
        - If the --regions argument is not specified, the default value "US" will be used.
        - The --package_listing argument is required.
        - The --output_prefix argument is optional. If not specified, it defaults to an empty string.
        - The --use_cached_html argument is optional. If not specified, it defaults to False
    """
    parser = argparse.ArgumentParser(description="This is a script that fetched data from google playstore for given packages and regions")
    parser.add_argument('--package_listing', type=str, required=True, help="File path to the file containing the listing of packages to fetch")
    parser.add_argument('--regions', type=lambda value: value.split(','), default="US", help="Listing of regions to fetch data from, ',' seperated list (e.g.: US,FI,JA). Defaults to US if none given")
    parser.add_argument('--output_prefix', default="", help="Optional input to prefix the output file names of the program, enabling seperate output files/folders. (e.g. FIN => FIN_raw_html_output). Defaults to nothing.")
    parser.add_argument('--use_cached_html', type=bool, default=False, help="Optional input to avoid fetching data from playstore. Instead use the existing cached html files.")
    args = parser.parse_args()
    return args.package_listing, args.regions, args.output_prefix, args.use_cached_html

if __name__ == "__main__":
    input_file, regions_list, output_prefix, use_cached_html = parse_console_arguments()
    main(input_file, regions_list, output_prefix, use_cached_html)