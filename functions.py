# Importing the libraries
# requests download the link > beutifulsoup read > urlib organize
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse


# Ignore these type of links
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")
DEFAULT_HEADERS = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (HTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
}


def is_skippable(href: str) -> bool:
    """Analyze if the page is skippable"""
    if not href:
        return True

    href = href.strip()

    if not href or href == "#" or href.startswith("#"): #Ignore #
        return True
    return href.startswith(SKIP_SCHEMES) #Ignore the values inside SKIP_SCHEMES

def normalize_link(base_url: str, href: str) -> str:
    """Transform links > /contact > https://site.com/contact and split the page"""
    abs_url = urljoin(base_url, (href or "").strip())
    parsed = urlparse(abs_url) # split the URL in many parts
    return parsed._replace(fragment="").geturl()

def fetch_html(url: str, timeout: int = 15) -> str | None:
    """Download the HTML from page"""
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True) #GET on http/https
        resp.raise_for_status()
        return resp.text
        # if an error occur, the HTML error is displayed

    except Exception:
        return None
        # any error return None

def extract_links(base_url: str, html: str) -> list[dict]:
    """Web scraping the page"""
    soup = BeautifulSoup(html, "html.parser") # Convert HTML in navegable structure
    links = [] # Storage links inside the variable

    for a in soup.find_all("a"): # Get all the <a>
        href = a.get("href")
        text = (a.get_text() or "").strip()

        if is_skippable(href):
            continue
        abs_url = normalize_link(base_url, href)
        links.append({"text": text or "(sem texto)", "href": href, "abs_url": abs_url})

    # Dedup remove
    seen = set() # verify duplicates
    unique = []
    for item in links:
        if item["abs_url"] not in seen:
            seen.add(item["abs_url"])
            unique.append(item)
    return unique

def check_link(url: str, timeout: int = 10) -> dict:
    """Check the link"""
    result = {
        "url": url,
        "status_code": None,
        "ok": False,
        "redirected": False,
        "final_url": None,
        "error": None,
        "method_used": None,
    }

    try:
        # HEAD first
        r = requests.head(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
        result["method_used"] = "HEAD"
        result["status_code"] = r.status_code
        result["final_url"] = r.url
        result["redirected"] = (r.url != url)

        if 200 <= r.status_code < 400:
            result["ok"] = True
            return result

        # Try GET if 405 or >=400
        if r.status_code >= 400 or r.status_code == 405:
            g = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
            result["method_used"] = "GET"
            result["status_code"] = g.status_code
            result["final_url"] = g.url
            result["redirected"] = (g.url != url)
            result["ok"] = 200 <= g.status_code < 400
            return result
    except requests.exceptions.SSLError as e:
        result["error"] = f"SSL error: {e}"
    except requests.exceptions.Timeout:
        result["error"] = "Timeout"
    except requests.exceptions.ConnectionError as e:
        result["error"] = f"Connection error: {e}"
    except Exception as e:
        result["error"] = f"Other error: {e}"
    return result