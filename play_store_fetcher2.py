import random
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

# read cached package names to avoid redundant requests
def read_cached_packages():
    if not os.path.exists(CACHE_FILE):
        return set()
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return set(line.strip().split(";")[0] for line in f if line.strip())

# read package names from the file
def read_package_names(file_path):
    package_names = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(";")
            if parts:
                package_names.append(parts[0])  # we get only the package name and not the type
    return package_names

# request Google Play Store
def send_request(URL: str):
    print(f"requesting {URL}")
    response = requests.get(URL)

    # use a random delay between 2 and 4 seconds to avoid getting blocked
    delay = random.uniform(2, 4)
    time.sleep(delay)

    if response.status_code == 200:
        return response
    elif response.status_code == 404:
        print(f"Error 404: Page not found for {URL}")
        return None
    else:
        print(f"Failed with status {response.status_code}")
        return None

# extract details for the app from HTML and use regular expressions to get the wanted information
def extract_app_info(text: str):
    text = text.replace(",", ".")
    rating_match = re.search(r'(\d+(\.\d+)?)\s*star', text, re.IGNORECASE)
    reviews_match = re.search(r'(\d+[A-Za-z\+]*?)\s*review', text, re.IGNORECASE)
    downloads_match = re.search(r'(\d+[A-Za-z\+]*?)\s*download', text, re.IGNORECASE)

    rating = rating_match.group(1) if rating_match else "Not found"
    reviews = reviews_match.group(1) if reviews_match else "Not found"
    downloads = downloads_match.group(1) if downloads_match else "Not found"

    return rating, reviews, downloads

# extract and get the app info directly from the HTML response
def get_app_info_from_html(PKG: str, html_text: str):
    soup = BeautifulSoup(html_text, 'html.parser')

    # extract rating, reviews and downloads
    raw_info = soup.find("div", class_="l8YSdd")
    if raw_info:
        rating, reviews, downloads = extract_app_info(raw_info.text.strip())
    else:
        print(f"Info not found for {PKG}.")
        rating, reviews, downloads = "Not found", "Not found", "Not found"

    # extract time of last update
    last_updated_info = soup.find("div", class_="xg1aie")
    if last_updated_info:
        last_updated_text = last_updated_info.text.strip()
    else:
        print(f"Update info not found for {PKG}.")
        last_updated_text = "Not found"

    return rating, reviews, downloads, last_updated_text

# save the data into the cache file and to CSV file
def save_to_cache_and_csv(PKG, rating, reviews, downloads, last_updated):
    # save first to cache file
    with open(CACHE_FILE, "a", encoding="utf-8") as file:
        file.write(f"{PKG};{rating};{reviews};{downloads};{last_updated}\n")

    # save to CSV file
    with open(OUTPUT_CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([PKG, rating, reviews, downloads, last_updated])

def main():
    package_names = read_package_names(CSV_FILE_PATH)
    cached_packages = read_cached_packages()

    # create CSV header if the file is empty
    if not os.path.exists(OUTPUT_CSV_FILE):
        with open(OUTPUT_CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Package Name', 'Rating', 'Reviews', 'Downloads', 'Last Updated'])

    for PKG_NAME in package_names:
        if PKG_NAME in cached_packages:
            print(f"Skipping {PKG_NAME}, already collected")
            continue

        url = URL_BEGIN + PKG_NAME
        r = send_request(url)

        # if the request was successful
        if r:
            rating, reviews, downloads, last_updated = get_app_info_from_html(PKG_NAME, r.text)
            save_to_cache_and_csv(PKG_NAME, rating, reviews, downloads, last_updated)
        else:
            print(f"Skipping {PKG_NAME} due to a failed request")

if __name__ == "__main__":
    main()

























