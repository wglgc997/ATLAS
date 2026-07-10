from urllib.parse import urldefrag, urljoin

from bs4 import BeautifulSoup

SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")
LINK_SELECTORS = (
    ("a[href]", "href", "anchor"),
    ("link[href]", "href", "resource"),
    ("script[src]", "src", "script"),
    ("img[src]", "src", "image"),
    ("iframe[src]", "src", "iframe"),
)


def extract_links_from_html(html: str, base_url: str) -> list[dict[str, str | None]]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[dict[str, str | None]] = []
    seen_urls: set[tuple[str, str]] = set()

    for selector, attribute, link_type in LINK_SELECTORS:
        for tag in soup.select(selector):
            raw_value = tag.get(attribute)

            if not isinstance(raw_value, str):
                continue

            link_value = raw_value.strip()

            if not link_value:
                continue

            if link_value.lower().startswith(SKIP_SCHEMES):
                continue

            absolute_url, _fragment = urldefrag(urljoin(base_url, link_value))
            dedupe_key = (absolute_url, attribute)

            if dedupe_key in seen_urls:
                continue

            seen_urls.add(dedupe_key)

            links.append(
                {
                    "url": absolute_url,
                    "link_text": tag.get_text(" ", strip=True) or None,
                    "link_type": link_type,
                    "source_attribute": attribute,
                }
            )

    return links
