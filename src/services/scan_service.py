from src.checker.link_checker import check_link
from src.crawler.browser_extractor import extract_links_with_browser
from src.schemas.scan import LinkResult, LinkStatus, ScanResponse
from src.config.settings import HTTP_TIMEOUT

from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urldefrag, urljoin, urlparse

INVALID_LINK_SCHEMES = {"mailto", "tel", "javascript", "data"}
IGNORED_UI_LINK_TEXTS = {
    "account",
    "au/en",
    "cart",
    "my account",
    "order status",
    "profile settings",
    "sign in",
}


def normalize_link_status(status: object) -> LinkStatus:
    if status == "Good":
        return LinkStatus.GOOD

    try:
        return LinkStatus(status)
    except ValueError:
        return LinkStatus.UNKNOWN_ERROR


def get_raw_link_value(link: dict) -> object:
    if "raw_url" in link:
        return link.get("raw_url")

    return link.get("url")


def get_invalid_link_reason(raw_link_value: object) -> str | None:
    if raw_link_value is None:
        return "Missing href attribute."

    if not isinstance(raw_link_value, str):
        return "The href attribute is not a text value."

    link_value = raw_link_value.strip()

    if not link_value:
        return "Empty href attribute."

    if link_value == "#":
        return 'The href attribute points only to "#".'

    scheme = urlparse(link_value).scheme.lower()

    if scheme in INVALID_LINK_SCHEMES:
        return f"The href uses a non-navigable scheme: {scheme}:."

    if scheme and scheme not in ALLOWED_SCHEMES:
        return f"The href uses an unsupported URL scheme: {scheme}:."

    return None


def normalize_label(value: object) -> str:
    if not isinstance(value, str):
        return ""

    return " ".join(value.split()).strip().lower()


def should_ignore_page_chrome_link(link: dict) -> bool:
    if link.get("ignored"):
        return True

    label = normalize_label(link.get("link_text"))
    location = normalize_label(link.get("source_location"))
    raw_link_value = get_raw_link_value(link)
    invalid_reason = get_invalid_link_reason(raw_link_value)

    if label in IGNORED_UI_LINK_TEXTS:
        return True

    if invalid_reason and "without visible text" in location:
        return True

    return False


def build_invalid_link_result(
        link: dict,
        page_url: str,
        reason: str,
) -> LinkResult:
    raw_link_value = get_raw_link_value(link)
    display_url = raw_link_value if isinstance(raw_link_value, str) else ""

    return LinkResult(
        url=display_url,
        final_url=None,
        http_status=None,
        status=LinkStatus.INVALID_LINK,
        redirect_chain=[],
        response_time_ms=0,
        error_message=reason,
        error_description=reason,
        technical_details=None,
        source_page=page_url,
        link_text=link.get("link_text"),
        link_type=link.get("link_type"),
        source_attribute=link.get("source_attribute") or "href",
        source_location=link.get("source_location"),
    )


def build_interaction_result(
        link: dict,
        page_url: str,
) -> LinkResult:
    raw_link_value = get_raw_link_value(link)
    display_url = raw_link_value if isinstance(raw_link_value, str) else ""
    interaction_status = link.get("interaction_status")
    detail = link.get("interaction_detail") or link.get("interaction_error")

    status = (
        LinkStatus.INTERACTIVE_ELEMENT
        if interaction_status == "interactive"
        else LinkStatus.INTERACTION_ERROR
    )

    return LinkResult(
        url=display_url,
        final_url=None,
        http_status=None,
        status=status,
        redirect_chain=[],
        response_time_ms=0,
        error_message=None if status == LinkStatus.INTERACTIVE_ELEMENT else detail,
        error_description=detail,
        technical_details=detail,
        source_page=page_url,
        link_text=link.get("link_text"),
        link_type=link.get("link_type"),
        source_attribute=link.get("source_attribute") or "href",
        source_location=link.get("source_location"),
    )


def build_link_result(
        link: dict,
        page_url: str,
        timeout: int = HTTP_TIMEOUT,
) -> LinkResult | None:
    link_url = link.get("url")

    if link.get("interaction_status") in {"interactive", "error"}:
        return build_interaction_result(
            link=link,
            page_url=page_url,
        )

    invalid_reason = link.get("invalid_reason") or get_invalid_link_reason(
        get_raw_link_value(link)
    )

    if invalid_reason:
        return build_invalid_link_result(
            link=link,
            page_url=page_url,
            reason=invalid_reason,
        )

    if not link_url:
        return build_invalid_link_result(
            link=link,
            page_url=page_url,
            reason="Missing href attribute.",
        )

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
        redirect_chain=checked_link.get("redirect_chain") or [],
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
SKIP_SCHEMES = {"vbscript"}
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
        if should_ignore_page_chrome_link(link):
            continue

        if not include_assets and link.get("link_type") in TECHNICAL_LINK_TYPES:
            continue

        raw_link_value = get_raw_link_value(link)
        invalid_reason = get_invalid_link_reason(raw_link_value)

        if link.get("interaction_status") == "navigated":
            link_url = normalize_link_url(link.get("url"), page_url)

            if not link_url:
                filtered_links.append(
                    {
                        **link,
                        "interaction_status": "error",
                        "interaction_error": "Click navigated to a non-HTTP URL.",
                    }
                )

                continue

            invalid_reason = None
            link = {
                **link,
                "url": link_url,
            }
        elif link.get("interaction_status") in {"interactive", "error"}:
            dedupe_key = "|".join(
                [
                    str(raw_link_value),
                    str(link.get("source_attribute")),
                    str(link.get("source_location")),
                    str(link.get("interaction_status")),
                ]
            )

            if dedupe_key in seen_urls:
                continue

            seen_urls.add(dedupe_key)
            filtered_links.append(link)

            continue

        if invalid_reason:
            dedupe_key = "|".join(
                [
                    str(raw_link_value),
                    str(link.get("source_attribute")),
                    str(link.get("source_location")),
                ]
            )

            if dedupe_key in seen_urls:
                continue

            seen_urls.add(dedupe_key)

            filtered_links.append(
                {
                    **link,
                    "url": raw_link_value if isinstance(raw_link_value, str) else "",
                    "invalid_reason": invalid_reason,
                }
            )

            continue

        link_url = normalize_link_url(link.get("url"), page_url)

        if not link_url:
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
        broken_statuses = {
            LinkStatus.BROKEN,
            LinkStatus.UNAUTHORIZED,
            LinkStatus.FORBIDDEN,
            LinkStatus.GONE,
            LinkStatus.SERVER_ERROR,
            LinkStatus.INVALID_LINK,
            LinkStatus.INTERACTION_ERROR,
            LinkStatus.REDIRECT_LOOP,
        }

        good = sum(
            result.status in {LinkStatus.GOOD, LinkStatus.INTERACTIVE_ELEMENT}
            for result in results
        )
        redirected = sum(result.status == LinkStatus.REDIRECTED for result in results)
        broken = sum(result.status in broken_statuses for result in results)
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
