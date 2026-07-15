from src.checker.link_checker import check_link
from src.crawler.browser_extractor import extract_links_with_browser
from src.schemas.scan import LinkResult, LinkStatus, ScanResponse
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def normalize_link_status(status: object) -> LinkStatus:
    if status == "Good":
        return "Good"

    if status == "Redirected":
        return "Redirected"

    if status == "Broken":
        return "Broken"

    return "Error"


def build_link_result(
        link: dict,
        page_url: str,
        timeout: int,
) -> LinkResult | None:
    link_url = link.get("url")

    if not link_url:
        return None

    checked_link = check_link(
        url=link_url,
        timeout=timeout,
    )

    status = normalize_link_status(checked_link.get("status"))

    return LinkResult(
        url=link_url,
        final_url=checked_link.get("final_url"),
        http_status=checked_link.get("http_status"),
        status=status,
        response_time_ms=checked_link.get("response_time_ms"),
        error_message=checked_link.get("error_message"),
        source_page=page_url,
        link_text=link.get("link_text"),
        link_type=link.get("link_type"),
        source_attribute=link.get("source_attribute"),
        source_location=link.get("source_location"),
    )

TECHNICAL_LINK_TYPES = {"resource", "script"}
IGNORED_DOMAINS = {
    "googletagmanager.com",
    "google-analytics.com",
    "doubleclick.net",
}

def is_same_domain(source_url: str, target_url: str) -> bool:
    source_host = urlparse(source_url).netloc.lower()
    target_host = urlparse(target_url).netloc.lower()

    return source_host == target_host

def is_ignored_domain(url: str) -> bool:
    host = urlparse(url).netloc.lower()

    return any(
        host == domain or host.endswith(f".{domain}")
        for domain in IGNORED_DOMAINS
    )

def filter_links(
        links: list[dict],
        page_url: str,
        include_assets: bool,
        include_external: bool,
) -> list[dict]:

    filtered_links = []

    for link in links:
        link_url = link.get("url")

        if not link_url:
            continue

        if not include_assets and link.get("link_type") in TECHNICAL_LINK_TYPES:
            continue

        if is_ignored_domain(link_url):
            continue

        if not include_external and not is_same_domain(link_url, page_url):
            continue

        filtered_links.append(link)

    return filtered_links

def scan_page(
        page_url: str,
        timeout: int = 10,
        max_workers: int = 12,
        include_assets: bool = False,
        include_external: bool = True,
) -> ScanResponse:

    links = extract_links_with_browser(page_url)
    links = filter_links(
        links=links,
        page_url=page_url,
        include_assets=include_assets,
        include_external=include_external,
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        scanned_results = executor.map(
            lambda link: build_link_result(link, page_url, timeout),
            links,
        )

        results = [
            result for result in scanned_results
            if result is not None
        ]

        good = sum(result.status == "Good" for result in results)
        redirected = sum(result.status == "Redirected" for result in results)
        broken = sum(result.status == "Broken" for result in results)
        error = sum(result.status == "Error" for result in results)

        return ScanResponse(
            source_page=page_url,
            total_links=len(results),
            good=good,
            redirected=redirected,
            broken=broken,
            error=error,
            results=results,
        )

