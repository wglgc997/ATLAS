from concurrent.futures import ThreadPoolExecutor

from src.services.link_filter import filter_links
from src.config.settings import HTTP_TIMEOUT
from src.crawler.browser_extractor import extract_links_with_browser
from src.schemas.scan import ScanResponse
from src.services.link_result_builder import build_link_result
from src.services.scan_summary import build_scan_response


def scan_page(
        page_url: str,
        timeout: int = HTTP_TIMEOUT,
        max_workers: int = 12,
        include_assets: bool = False,
        include_external: bool = True,
) -> ScanResponse:
    links = extract_links_with_browser(page_url)

    filtered_links = filter_links(
        links=links,
        page_url=page_url,
        include_assets=include_assets,
        include_external=include_external,
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        scanned_results = executor.map(
            lambda link: build_link_result(link, page_url, timeout),
            filtered_links,
        )

        results = [
            result for result in scanned_results
            if result is not None

        ]

        return build_scan_response(
            source_page=page_url,
            results=results
        )

