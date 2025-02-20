import requests
from bs4 import BeautifulSoup

URL_BEGIN = "https://play.google.com/store/apps/details?id="
PKG_NAME = "com.android.chrome"
CACHED_FILES = []
RAW_HTML_DIR = "raw_html"

# Should maybe read the html filenames into the cached_files
# instead just reading the cached_files.txt
with open("cached_files.txt", "r") as f:
    content = f.read()
    CACHED_FILES = content.split(",")


def send_request(URL: str):
    print(f"Requesting {URL}")
    response = requests.get(URL)

    if response.status_code == 200:
        return response
    else:
        print(f"Failed with status {response.status_code}")
        return


def print_info(PKG: str):
    with open(f"{RAW_HTML_DIR}_{PKG}.html", "r", encoding='utf-8') as f:
        html = f.read()
        soup = BeautifulSoup(html, 'html.parser')

        print(f"PACKAGE INFO: {PKG}")
        print("Title: " + soup.title.string)

        res = soup.find_all("div", {"class": "ClM7O"})
        for re in res:
            print(re.text)

        # print(soup.prettify())

    return


def Main():
    if PKG_NAME not in CACHED_FILES:
        r = send_request(URL_BEGIN + PKG_NAME)

        if r.status_code == 200:
            html = r.text
            open(f"{RAW_HTML_DIR}_{PKG_NAME}.html", "x")
            with open(f"{RAW_HTML_DIR}_{PKG_NAME}.html", "w", encoding='utf-8') as f:
                f.write(html)

            # Caching files should probably happen once everything else succeeds
            CACHED_FILES.append(PKG_NAME)
            with open("cached_files.txt", "w") as f:
                f.write(PKG_NAME + ",")
        else:
            return

    else:
        print(f"Skipping {PKG_NAME}... already requested")

    print_info(PKG_NAME)


if __name__ == "__main__":
    Main()