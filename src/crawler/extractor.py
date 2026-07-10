from urllib.parse import urljoin
from bs4 import BeautifulSoup

SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")


def extract_links_from_html(html: str, base_url: str):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for tag in soup.select("a[href]"):
        href = tag.get("href")

        if not href:
            continue

        if href.startswith(SKIP_SCHEMES):
            continue

        links.append({
            "url": urljoin(base_url, href),
            "text": tag.get_text(strip=True) or None,
            "link_type": "anchor",
            "source_attribute": "href",
        })

    return links