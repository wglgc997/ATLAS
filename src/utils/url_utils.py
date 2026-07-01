from urllib.parse import urljoin, urlparse

from src.config.constant import SKIP_SCHEMES


def get_depth(url):

    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    return len([p for p in parts if p])


def url_https(url):
    """ "Link have HTTPS?"""
    return url.startswith("https://")


def is_internal(base_url, target_url):

    base_domain = urlparse(base_url).netloc
    target_domain = urlparse(target_url).netloc
    return base_domain == target_domain


def is_skippable(href: str) -> bool:
    """Analyze if the page is skippable"""
    if not href:
        return True

    href = href.strip()

    if not href or href == "#" or href.startswith("#"):  # Ignore #
        return True
    return href.startswith(SKIP_SCHEMES)  # Ignore the values inside SKIP_SCHEMES


def normalize_link(base_url: str, href: str) -> str:
    """Transform links > /contact > https://site.com/contact and split the page"""
    abs_url = urljoin(base_url, (href or "").strip())
    parsed = urlparse(abs_url)  # split the URL in many parts
    return parsed._replace(fragment="").geturl()


def validate_url(url):
    """Validate the URL checking if have http/https"""
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)
