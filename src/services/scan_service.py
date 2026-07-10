from src.checker.link_checker import check_link
from src.crawler.browser_extractor import extract_links_with_browser


def scan_page(page_url: str, timeout: int = 10) -> dict:
    """
    Extract all links from a page, validate them and
    return a complete scan summary.
    """

    # Extract links after the page is rendered by the browser.
    links = extract_links_with_browser(page_url)

    results = []

    # Validate every extracted link.
    for link in links:
        link_url = link.get("url")

        if not link_url:
            continue

        checked_link = check_link(
            url=link_url,
            timeout=timeout,
        )

        result = {
            "url": link["url"],
            "final_url": checked_link.get("final_url"),
            "http_status": checked_link.get("http_status"),
            "status": checked_link.get("status"),
            "response_time_ms": checked_link.get("response_time_ms"),
            "error_message": checked_link.get("error_message"),
            "source_page": page_url,
            "link_text": link.get("link_text"),
            "link_type": link.get("link_type"),
            "source_attribute": link.get("source_attribute"),
        }

        results.append(result)

    # Count links by final category.
    good = sum(
        result["status"] == "Good"
        for result in results
    )

    redirected = sum(
        result["status"] == "Redirected"
        for result in results
    )

    broken = sum(
        result["status"] == "Broken"
        for result in results
    )

    return {
        "source_page": page_url,
        "total_links": len(results),
        "good": good,
        "redirected": redirected,
        "broken": broken,
        "results": results,
    }