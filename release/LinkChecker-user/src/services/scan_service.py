from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        progress_callback: Callable[[str, int, int], None] | None = None,
) -> ScanResponse:
    if progress_callback:
        progress_callback("rendering", 0, 0)

    links = extract_links_with_browser(page_url)

    if progress_callback:
        progress_callback("extracting", 0, 0)

    filtered_links = filter_links(
        links=links,
        page_url=page_url,
        include_assets=include_assets,
        include_external=include_external,
    )

    total_links = len(filtered_links)
    if progress_callback:
        progress_callback("checking", total_links, 0)

    results_by_index: list = [None] * total_links
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(build_link_result, link, page_url, timeout): index
            for index, link in enumerate(filtered_links)
        }

        for completed_links, future in enumerate(as_completed(futures), start=1):
            results_by_index[futures[future]] = future.result()
            if progress_callback:
                progress_callback("checking", total_links, completed_links)

    if progress_callback:
        progress_callback("building", total_links, total_links)

    return build_scan_response(
        source_page=page_url,
        results=[result for result in results_by_index if result is not None],
    )

