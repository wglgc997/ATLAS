from src.checker.link_checker import check_link
from src.crawler.browser_extractor import extract_links_with_browser
from src.schemas.scan import LinkResult, LinkStatus, ScanResponse
from src.config.settings import HTTP_TIMEOUT

from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urldefrag, urljoin, urlparse

def normalize_link_status(status: object) -> LinkStatus:
    try:
        return LinkStatus(status)
    except ValueError:
        return LinkStatus.UNKNOWN_ERROR


def build_link_result(
        link: dict,
        page_url: str,
        timeout: int = HTTP_TIMEOUT,
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
        error_description=checked_link.get("error_description"),
        technical_details=checked_link.get("technical_details"),
        source_page=page_url,
        link_text=link.get("link_text"),
        link_type=link.get("link_type"),
        source_attribute=link.get("source_attribute"),
        source_location=link.get("source_location"),
    )

TECHNICAL_LINK_TYPES = {"resource", "script", "image", "iframe"}
SKIP_SCHEMES = {"mailto", "tel", "javascript", "data", "vbscript"}
ALLOWED_SCHEMES = {"http", "https"}
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

def normalize_link_url(link_url: object, page_url: str) -> str | None:
    if not isinstance(link_url, str):
        return None

    link_url = link_url.strip()

    if not link_url or link_url.startswith("#"):
        return None

    parsed_url = urlparse(link_url)

    if parsed_url.scheme.lower() in SKIP_SCHEMES:
        return None

    absolute_url, _fragment = urldefrag(urljoin(page_url, link_url))
    absolute_scheme = urlparse(absolute_url).scheme.lower()

    if absolute_scheme not in ALLOWED_SCHEMES:
        return None

    return absolute_url

def filter_links(
        links: list[dict],
        page_url: str,
        include_assets: bool,
        include_external: bool,
) -> list[dict]:

    filtered_links = []
    seen_urls: set[str] = set()

    for link in links:
        link_url = normalize_link_url(link.get("url"), page_url)

        if not link_url:
            continue

        if not include_assets and link.get("link_type") in TECHNICAL_LINK_TYPES:
            continue

        if is_ignored_domain(link_url):
            continue

        if not include_external and not is_same_domain(link_url, page_url):
            continue

        if link_url in seen_urls:
            continue

        seen_urls.add(link_url)

        filtered_link = {
            **link,
            "url": link_url,
        }

        filtered_links.append(filtered_link)

    return filtered_links

def scan_page(
        page_url: str,
        timeout: int = HTTP_TIMEOUT,
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

        error_statuses = {
            LinkStatus.SSL_ERROR,
            LinkStatus.TIMEOUT,
            LinkStatus.CONNECTION_ERROR,
            LinkStatus.DNS_ERROR,
            LinkStatus.UNKNOWN_ERROR,
        }

        good = sum(result.status == LinkStatus.GOOD for result in results)
        redirected = sum(result.status == LinkStatus.REDIRECTED for result in results)
        broken = sum(result.status == LinkStatus.BROKEN for result in results)
        error = sum(result.status in error_statuses for result in results)

        return ScanResponse(
            source_page=page_url,
            total_links=len(results),
            good=good,
            redirected=redirected,
            broken=broken,
            error=error,
            results=results,
        )

