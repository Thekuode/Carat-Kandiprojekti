# Playstore data fetcher

## About
This project was originally built to fetch data from the Google Play Store for applications discovered in the [Carat project](https://www.cs.helsinki.fi/group/carat/data-sharing/).  
It takes as input a CSV file containing a list of applications and fetches the following data points for them:  
- Rating displayed for the application on the store page.  
- Number of reviews displayed for the application on the store page.  
- Number of downloads displayed for the application on the store page.  
- Date of last update for the application displayed on the store page.  

## Install
Requirements for the project are:  
- Python version 3.7+  
- Packages listed in the `requirements.txt`

The packages can be installed using pip with the following command:  
`pip install -r requirements.txt`

## Usage
This section provides both a quick start guide and detailed descriptions of the different aspects of using the tool.

### Quick start
Given a CSV file with application package IDs in the first column, the script can be used to fetch data for them using the following command:  
`python play_store_fetcher.py --package_listing path/to/packages.csv --regions US,FI`

This will output Play Store data from the regions Finland and United States for the given package list.

### Input file requirements
The script expects the following from the input CSV file:
- The application package ID should be provided in the first column. The rest of the row is ignored.
- The file should be delimited by a `;`.
- Any potential process ID additions to the package ID should be separated by a `:`.

Given these conditions, the script will be able to read the required information from the input CSV file.

### Available console commands
The script can be controlled with the following console commands:  
`--package_listing` Required String. The file path to the input CSV file. E.g., `--package_listing path/to/csv.csv`  
`--regions` Optional String. A comma-separated list of two-letter ISO 3166-1 alpha-2 country codes. Defaults to `US` if not provided. E.g., `--regions JA,FI,US`  
`--output_prefix` Optional String. The prefix for the output files. This can be a relative folder prefix or a simple filename prefix. Any folders will be created. Defaults to empty. E.g., `--output_prefix fetched_data/`  
`--use_cached_html` Optional Bool. If set, the script will prefer the cached HTML file over fetching new data from the Play Store. This is useful for rerunning lists. E.g., `--use_cached_html True`

### Console outputs
During the fetching process, the following information will be displayed in the console:
- Initialization error message (e.g., "Did not find input file").
- The current package/region being collected.
- The status of the current package fetch (Success, Not found, Error).
- The time it took to fetch the package list.

Any information related to the packages will also be logged in an output file.

## Output files
The script generates four CSV files and a folder where cached HTML files from the Google Play Store pages are stored. The location of these files is affected by the console command `--output_prefix`.  
The four output CSV files are:
- `cached_pkgs.csv`: This CSV file is used internally by the script to avoid making duplicate requests.
- `pkg_data_found.csv`: This CSV file contains the extracted information for the packages from their Google Play Store pages.
- `pkg_error.csv`: This CSV file contains a listing of any errors that occurred, the packages related to those errors, and any additional information about the errors.
- `pkg_missing.csv`: This CSV file contains a listing of all packages that returned a 404 HTTP status from the Google Play Store.

Cached HTML files are placed in the folder `raw_html_output`. The file name indicates the package name and the region from where the page was fetched.

### Structure of `cached_pkgs.csv`
This CSV file is delimited by a `;`. The columns are:
- Package ID: The name of the package. The value is a string.
- Region code: The region where the data was fetched from. The value is a string.

Example row:  
`com.google.android.videos;US`

### Structure of `pkg_data_found.csv`
This CSV file is delimited by a `;`. The columns are:
- Package ID: The package that the data is related to. The value is a string.
- Region code: The region that the data is related to. The value is a string.
- Rating: The rating value displayed on the package's store page. If the value is not extractable, the value 'Not Found' is used. The value is an integer or floating point.
- Review count: The number of reviews left for the package displayed on the store page. If the value is not extractable, the value 'Not Found' is used. The value is a string.
- Download count: The number of downloads for the package, displayed on the store page. If the value is not extractable, the value 'Not Found' is used. The value is a string.
- Last updated: The date of the last update for the package. If the value is not extractable, the value 'Not Found' is used. The value is a string or datetime in the format 'Dec 01, 2024'.

Example row:  
`com.google.android.videos;US;3.9;2.64M;5B+;Mar 10, 2025`

### Structure of `pkg_error.csv`
This CSV file is delimited by a `;`. The columns are:
- Package ID: The package that the error is related to. The value is a string.
- Region code: The region that the error is related to. The value is a string.
- HTTP Status: The status code returned for the possible requests. The value is an integer.
- URL: The URL that was requested when the error occurred. The value is a string.
- Exception message: The exception message provided when the error occurred.

Example row:  
`edu.berkeley.cs.amplab.carat.android;FI;500;https://play.google.com/store/apps/details?id=edu.berkeley.cs.amplab.carat.android&gl=FI&hl=en;`

### Structure of `pkg_missing.csv`
This CSV file is delimited by a `;`. The columns are:
- Package ID: The package that the data is related to. The value is a string.
- Region code: The region that the data is related to. The value is a string.
- HTTP Status: The status code returned for the requests. The value is an integer.
- URL: The URL that was requested. The value is a string.

Example row:  
`edu.berkeley.cs.amplab.carat.android;FI;404;https://play.google.com/store/apps/details?id=edu.berkeley.cs.amplab.carat.android&gl=FI&hl=en`