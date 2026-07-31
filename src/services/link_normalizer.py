from urllib.parse import urlparse, urljoin, urldefrag

INVALID_LINK_SCHEMES = {"mailto", "tel", "javascript", "data"}
SKIP_SCHEMES = {"vbscript"}
ALLOWED_SCHEMES = {"http", "https"}
IGNORED_DOMAINS = {
    "googletagmanager.com",
    "google-analytics.com",
    "doubleclick.net",
}

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