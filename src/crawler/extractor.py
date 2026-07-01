from bs4 import BeautifulSoup
from src.utils.url_utils import is_skippable, normalize_link


def extract_links(base_url: str, html: str) -> list[dict]:
    """Web scraping the page"""
    soup = BeautifulSoup(html, "html.parser")  # Convert HTML in navegable structure
    links = []  # Storage links inside the variable

    for a in soup.find_all("a"):  # Get all the <a>
        href = a.get("href")
        text = (a.get_text() or "").strip()

        if is_skippable(href):
            continue
        abs_url = normalize_link(base_url, href)
        links.append(
            {
                "text": text or "(sem texto)",
                "href": href,
                "abs_url": abs_url,
                "source_page": base_url,
            }
        )

    # Dedup remove
    seen = set()  # verify duplicates
    unique = []
    for item in links:
        if item["abs_url"] not in seen:
            seen.add(item["abs_url"])
            unique.append(item)
    return unique
