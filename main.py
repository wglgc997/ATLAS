import argparse
import concurrent.futures
import csv
from urllib.parse import urlparse
from functions import check_link, extract_links, fetch_html

try:
    from colorama import Fore, Style, init
except ImportError:
    class noColorama:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET_ALL = ""
        BRIGHT = DIM = NORMAL = RESET_ALL = ""
    Fore = Style = noColorama()

    def init():
        return None


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
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=20,
        help="Number of threads to use",
    )
    parser.add_argument(
        "-T",
        "--timeout",
        type=int,
        default=10,
        help="Seconds to wait before timing out",
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        help="Path to csv file",
    )
    parser.add_argument(
        "--only-broken",
        action="store_true",
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
        "Text": link["text"],
        "Found URL": link["href"],
        "Absolute URL": result["url"],
        "Status": result["status_code"],
        "OK": result["ok"],
        "Redirected": result["redirected"],
        "Final URL": result["final_url"],
        "Method": result["method_used"],
        "Error":result["error"],
    }

def result_label(row):
    """Visual/colors classification"""
    if row["Error"]:
        return f"{Fore.RED}[ERROR]{Style.RESET_ALL}"

    if row["OK"] and row["Redirected"]:
        return f"{Fore.YELLOW}[REDIRECTED]{Style.RESET_ALL}"

    if row["OK"]:
        return f"{Fore.GREEN}[OK]{Style.RESET_ALL}"
    return f"{Fore.RED}[BROKEN]{Style.RESET_ALL}"
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
        "Text",
        "Found URL",
        "Absolute URL",
        "Status",
        "OK",
        "Redirected",
        "Final URL",
        "Method",
        "Error",
    ]

    with open(path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)

def check_links(links, threads, timeout, only_broken):
    rows = []
    done = 0
    total = len(links)

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
def main():
    init()
    args = parse_args()

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





