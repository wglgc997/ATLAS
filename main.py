import argparse
import concurrent.futures
<<<<<<< HEAD
import csv
from urllib.parse import urlparse
from functions import check_link, extract_links, fetch_html
=======
import csv,os
import re
import uuid
from urllib.parse import urlparse
from functions import check_link, extract_links, fetch_html, DEFAULT_HEADERS, get_depth, url_https, is_internal, status_category
from datetime import datetime

REGIONS = r"^[a-z]{2}-[a-z]{2}$"
VALID_REGIONS = [
    "en-uk",
    "en-ie",
    "da-dk",
    "de-de",
    "de-at",
    "de-ch",
    "es-es",
    "fr-fr",
    "fr-be",
    "fr-ch",
    "it-it",
    "nl-nl",
    "nl-be",
    "no-no",
    "sv-se",
    "hu-hu",
    "ro-ro",
    "tr-tr",
    "pl-pl",
    "en-ng",
    "en-bg",
    "en-yu",
    "en-hr",
    "ja-jp",
    "ko-kr",
    "zh-cn",
    "zh-tw",
    "zh-hk",
    "en-hk",
    "en-au",
    "en-nz",
    "en-in",
    "en-sg",
    "en-pk",
    "en-ph",
    "en-id",
    "en-vn",
    "en-th",
    "en-us",
    "en-ca",
    "fr-ca",
    "en/es",
    "es/ag",
    "es/ai",
    "es/an",
    "es/ar",
    "es/aw",
    "es/bb",
    "es/bm",
    "es/bo",
    "es/bs",
    "es/bz",
    "es/cl",
    "es/co",
    "es/cr",
    "es/dm",
    "es/do",
    "es/ec",
    "es/es",
    "es/gd",
    "es/gt",
    "es/gy",
    "es/hn",
    "es/ht",
    "es/jm",
    "es/kn",
    "es/ky",
    "es/la",
    "es/lc",
    "es/mx",
    "es/ni",
    "es/pa",
    "es/pe",
    "es/pr",
    "es/py",
    "es/sr",
    "es/sv",
    "es/tc",
    "es/tt",
    "es/ue",
    "es/us",
    "es/uy",
    "es/vc",
    "es/ve",
    "es/vg",
    "es/vi",
    ]


>>>>>>> ac6c9ce (new functions)

try:
    from colorama import Fore, Style, init
except ImportError:
<<<<<<< HEAD
    class noColorama:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET_ALL = ""
        BRIGHT = DIM = NORMAL = RESET_ALL = ""
    Fore = Style = noColorama()
=======
    class _NoColor:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET_ALL = ""
        BRIGHT = DIM = NORMAL = RESET_ALL = ""
    Fore = Style = _NoColor()
>>>>>>> ac6c9ce (new functions)

    def init():
        return None

<<<<<<< HEAD

# Functions

def parse_args():
    """Create and parse command line arguments."""
    parser = argparse.ArgumentParser(description="Check links here")
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        type=str,
        help="Example https://www.google.com",
    )
=======
def parse_args():
    """Create the CLI environment and catch the URL """
    parser = argparse.ArgumentParser(
        description="Check broken links from CVC pre-live environment."
    )
    parser.add_argument(
        "--url",
        nargs="?",
        default=None,
        help="Page URL to scan. Example: https://example.com")
>>>>>>> ac6c9ce (new functions)
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=20,
<<<<<<< HEAD
        help="Number of threads to use",
    )
    parser.add_argument(
        "-T",
        "--timeout",
        type=int,
        default=10,
        help="Seconds to wait before timing out",
=======
        help="Number of links to check at the same time. Default: 20",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Seconds to wait before a link request fails. Default: 10",
>>>>>>> ac6c9ce (new functions)
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
<<<<<<< HEAD
        help="Path to csv file",
=======
        help="Optional path to save the result as CSV.",
>>>>>>> ac6c9ce (new functions)
    )
    parser.add_argument(
        "--only-broken",
        action="store_true",
<<<<<<< HEAD
        help="Shows only the broken links found."
    )

    return parser.parse_args()
def validate_url(url):
    """Validate the url provided by parse."""
    parsed = urlparse(url) #splits a URL into parts
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)
def build_row(link, result):
    """Build a row from the link."""
    return {
=======
        help="Print only broken links and errors.",
    )

    parser.add_argument(
        "--file",
        help="Read a file"
    )
    return parser.parse_args()

def validate_url(url):
    """Validate the URL checking if have http/https"""
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)

def extract_region(url):
    """Extract the region from link. Ex :PT-BR"""
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    if not parts:
        return "unknown"
    first_part = parts[0].lower()

    if not re.match(REGIONS, first_part):
        return  "unknown"

    if first_part in VALID_REGIONS:
        return first_part
    # if (
    # first_part in EMEA_LINKS
    #     or first_part in NA_LINKS
    #     or first_part in LATAM_LINKS
    #     or first_part in APJ_LINKS
    # ):
        return first_part



    return "unknown"

def build_row(link, result, crawl_id):
    """Create the fields"""
    return {
        "Timestamp": datetime.now().isoformat(),
        "Crawl ID": crawl_id,
        "Region": extract_region(result["url"]),
        "Depth": get_depth(result["url"]),
        "HTTPS": url_https(result["url"]),
        "Internal": is_internal(link["abs_url"],result["url"]),
>>>>>>> ac6c9ce (new functions)
        "Text": link["text"],
        "Found URL": link["href"],
        "Absolute URL": result["url"],
        "Status": result["status_code"],
        "OK": result["ok"],
        "Redirected": result["redirected"],
        "Final URL": result["final_url"],
        "Method": result["method_used"],
<<<<<<< HEAD
        "Error":result["error"],
=======
        "Error": result["error"],
        "Response_time": result.get("response_time"),
        "Status Category": status_category(result["status_code"]),

>>>>>>> ac6c9ce (new functions)
    }

def result_label(row):
    """Visual/colors classification"""
    if row["Error"]:
        return f"{Fore.RED}[ERROR]{Style.RESET_ALL}"

    if row["OK"] and row["Redirected"]:
<<<<<<< HEAD
        return f"{Fore.YELLOW}[REDIRECTED]{Style.RESET_ALL}"
=======
        return f"{Fore.YELLOW}[REDIRECT]{Style.RESET_ALL}"
>>>>>>> ac6c9ce (new functions)

    if row["OK"]:
        return f"{Fore.GREEN}[OK]{Style.RESET_ALL}"
    return f"{Fore.RED}[BROKEN]{Style.RESET_ALL}"
<<<<<<< HEAD
def print_result(row, only_broken=False):
    """Show the result"""
    is_broken = row["Error"] or not row ["OK"]
    if only_broken and not is_broken:
        return

    status = row["Status"] if row["Status"]is not None else "-"
    error = f" | {row['Error']}" if row["Error"] else ""
    final_url = ""
    if row ["Redirected"] and row["Final URL"]:
        final_url = f" -> {row["Final URL"]}"

    print(f"{result_label(row):18} {status!s:4} {row['Absolute URL']}{final_url}{error}")
def csv(path,row):
    """Print a csv file"""
    fields = [ #Push from result_label
=======

def print_result(row, only_broken=False):
    """"Print all the results"""
    is_broken = row["Error"] or not row["OK"]
    if only_broken and not is_broken:
        return

    status = row["Status"] if row["Status"] is not None else "-"
    error = f" | {row['Error']}" if row["Error"] else ""
    final_url = ""
    if row["Redirected"] and row["Final URL"]:
        final_url = f" -> {row['Final URL']}"

    print(f"{result_label(row):18} {status!s:>4}  {row['Absolute URL']}{final_url}{error}")

def save_csv(path, rows):
    """Create and structure the CSV file"""
    fieldnames = [
        "Crawl ID",
        "Timestamp",
        "Region",
>>>>>>> ac6c9ce (new functions)
        "Text",
        "Found URL",
        "Absolute URL",
        "Status",
        "OK",
        "Redirected",
        "Final URL",
        "Method",
        "Error",
<<<<<<< HEAD
    ]

    with open(path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)

def check_links(links, threads, timeout, only_broken):
=======
        "Response_time",
        "Depth",
        "HTTPS",
        "Internal",
        "Status Category",
    ]

    file_exist = os.path.isfile(path) # Verify if csv file already exist

    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exist: # Write just one time
            writer.writeheader()


        writer.writerows(rows) # Save the data

def check_links(links, threads, timeout, only_broken, crawl_id):
    """Execute multiple threads at same time > speed"""
>>>>>>> ac6c9ce (new functions)
    rows = []
    done = 0
    total = len(links)

<<<<<<< HEAD
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=threads) as executor:

        futures = {
            executor.submit(
                check_link,
                link["abs_url"],
                timeout
            ): link
            for link in links}

    for future in concurrent.futures.as_completed(futures):
        link = futures[future]
        result = future.result()
        row = build_row(link, result)
        rows.append(row)
        done += 1

        print_result(row, only_broken=only_broken)

        # try:
        #     result = future.result()
        #
        # except Exception as e:
        #     result = {
        #         "url": link["abs_url"],
        #         "status_code": None,
        #         "ok": False,
        #         "redirected": False,
        #         "final_url": False,
        #         "error": str(e),
        #         "method": None,
        #     }

        row = build_row(link, result)
        rows.append(row)
        done += 1

        print_result(row, only_broken=only_broken)

    if done % 10 == 0 or done == total:
        print(
            f"{Fore.CYAN}"
            f"Progress: {done}/{total}"
            f"{Style.RESET_ALL}"
        )
    return rows
=======
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(check_link, link["abs_url"], timeout): link
            for link in links
        }

        for future in concurrent.futures.as_completed(futures):
            link = futures[future]
            result = future.result()
            row = build_row(link, result, crawl_id)
            rows.append(row)
            done += 1

            print_result(row, only_broken=only_broken)

            if done % 10 == 0 or done == total:
                print(f"{Fore.CYAN}Progress: {done}/{total}{Style.RESET_ALL}")

        return rows

def read_file(path):
    """"Config the read mode """
    with open(path, "r", encoding="utf-8") as file:

        return [
            line.strip()
            for line in file
            if line.strip()
        ]

>>>>>>> ac6c9ce (new functions)
def main():
    init()
    args = parse_args()

<<<<<<< HEAD
    if not validate_url(args.url):
        args.url = input(
            f"{Fore.CYAN}Type the URL: {Style.RESET_ALL}"
        )

    if not validate_url(args.url):
        print(
            f"{Fore.RED}Invalid URL. Use something like: "
            f"https://example.com{Style.RESET_ALL}"
        )
        return 1

    print(
        f"{Fore.CYAN}Checking page:{Style.RESET_ALL} {args.url}"
    )

    html = fetch_html(
        args.url,
        timeout=args.timeout
    )

    if not html:
        print(
            f"{Fore.RED}Could not download the page HTML."
            f"{Style.RESET_ALL}"
        )
        return 1

    links = extract_links(args.url, html)

    if not links:
        print(
            f"{Fore.YELLOW}No links found on this page."
            f"{Style.RESET_ALL}"
        )
        return 0

    print(
        f"{Fore.CYAN}Found {len(links)} links. Checking..."
        f"{Style.RESET_ALL}"
    )

    rows = check_links(
        links,
        args.threads,
        args.timeout,
        args.only_broken
    )

    broken = [
        row for row in rows
        if row["Error"] or not row["OK"]
    ]

    print()

    print(f"{Fore.CYAN}Finished.{Style.RESET_ALL}")

    print(
        f"Broken links: "
        f"{Fore.RED}{len(broken)}{Style.RESET_ALL} / {len(rows)}"
    )

    if args.csv_path:
        save_csv(args.csv_path, rows)

        print(
            f"{Fore.GREEN}CSV saved:{Style.RESET_ALL} "
            f"{args.csv_path}"
        )

    return 0
if __name__ == "__main__":
    raise SystemExit(main())





=======
    urls = []

    if args.file:
        urls = read_file(args.file)
    elif args.url:
        urls = [args.url]
    else:
        print("Provide a URL or --file")
        return 1

    crawl_id = str(uuid.uuid4())
    all_rows = []

    for url in urls:
        print(f"{Fore.CYAN}Checking page:{Style.RESET_ALL} {url}")
        html = fetch_html(url, timeout=args.timeout)

        if not html:
            print(f"{Fore.RED}Could not download the page HTML.{Style.RESET_ALL}")
            continue
        links = extract_links(url, html)

        if not links:
            print("Not links found")
            continue

        print(f"Found{len(links)}links")

        rows = check_links(
            links,
            args.threads,
            args.timeout,
            args.only_broken,
            crawl_id
        )

        all_rows.extend(rows)

        if args.csv_path:
            save_csv(args.csv_path, all_rows)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
>>>>>>> ac6c9ce (new functions)
