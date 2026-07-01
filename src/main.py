import logging
import uuid


from django.utils.log import configure_logging

from src.cli.arguments import parse_args
from src.crawler.extractor import extract_links
from src.crawler.fetcher import fetch_html
from src.services.csc_service import save_csv
from src.services.scan_service import check_links
from src.utils.file_utils import read_file
from src.utils.logger import setup_logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

try:
    from colorama import Fore, Style, init
except ImportError:

    class _NoColor:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET_ALL = ""
        BRIGHT = DIM = NORMAL = RESET_ALL = ""

    Fore = Style = _NoColor()

    def init():
        return None


def main() -> int:

    init()

    setup_logging()

    args = parse_args()

    logger.info("Link Checker started")

    if args.file:
        urls = read_file(args.file)
        logger.info("Loaded % URL(s) from file: %s", len(urls), args.file)

    elif args.url:
        urls = [args.url]
        logger.info("Loaded single URL %s", args.url)

    else:
        logger.error("No URL or input file provided")
        print("Provide a URL or --file")
        return 1

    crawl_id = str(uuid.uuid4())
    logger.info("Crawl ID created: %s", crawl_id)

    for url in urls:
        print(f"{Fore.CYAN}Checking page:{Style.RESET_ALL} {url}")
        logger.info("Checking page: %s", url)

        html = fetch_html(url, timeout=args.timeout)

        if not html:
            print(f"{Fore.RED}Could not download the page HTML.{Style.RESET_ALL}")
            continue

        links = extract_links(url, html)

        if not links:
            logger.warning("No links found on page> %s", url)
            print("Not links found")
            continue

        print(f"Found{len(links)}links")
        logger.info("Found %s link(s) on page: %s", len(links), url)

        rows = check_links(
            links=links,
            threads=args.threads,
            timeout=args.timeout,
            only_broken=args.only_broken,
            crawl_id=crawl_id,
        )

        logger.info(
            "Scan completed | crawl_id=%s | page=%s | checked_links=%s",
            crawl_id,
            url,
            len(rows)
        )


        if args.csv_path:
            save_csv(args.csv_path, rows)
            logger.info("CSV saved: %s", args.csv_path)

    logger.info("Link Checker finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
