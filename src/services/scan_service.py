
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from src.checker.link_checker import check_link
from src.config.regions import extract_region
from src.utils.console import print_result
from src.utils.status_utils import status_category
from src.utils.url_utils import get_depth, url_https, is_internal


def check_links(links, threads, timeout, only_broken, crawl_id):
    """Execute multiple threads at same time > speed"""
    rows = []
    done = 0
    total = len(links)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(check_link, link["abs_url"], timeout): link
            for link in links
        }

        for future in as_completed(futures):
            link = futures[future]
            result = future.result()

            row = build_row(link, result, crawl_id)
            rows.append(row)
            done += 1

            print_result(row, only_broken=only_broken)

            if done % 10 == 0 or done == total:
                print(f"{Fore.CYAN}Progress: {done}/{total}{Style.RESET_ALL}")

        return rows


def build_row(link, result, crawl_id):
    """Create the fields"""
    return {
        "Timestamp": datetime.now().isoformat(),
        "Crawl ID": crawl_id,
        "Region": extract_region(result["url"]),
        "Depth": get_depth(result["url"]),
        "HTTPS": url_https(result["url"]),
        "Internal": is_internal(link["abs_url"], result["url"]),
        "Source Page": link["source_page"],
        "Text": link["text"],
        "Found URL": link["href"],
        "Absolute URL": result["url"],
        "Status": result["status_code"],
        "OK": result["ok"],
        "Redirected": result["redirected"],
        "Final URL": result["final_url"],
        "Method": result["method_used"],
        "Error": result["error"],
        "Response_time": result.get("response_time"),
        "Status Category": status_category(result["status_code"]),
    }
