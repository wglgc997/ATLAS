import time
from typing import TypedDict

import requests
from src.config.settings import DEFAULT_HEADERS


class LinkCheckResult(TypedDict):
    timestamp: None
    crawl_id: None
    url: str
    status_code: int | None
    ok: bool
    redirected: bool
    final_url: str | None
    error: str | None
    method_used: str | None
    response_time: float | None
    depth: None
    https: None
    internal: None
    status_category: None


def check_link(url: str, timeout: int = 10) -> LinkCheckResult:
    """Check the link"""
    result: LinkCheckResult = {
        "timestamp": None,
        "crawl_id": None,
        "url": url,
        "status_code": None,
        "ok": False,
        "redirected": False,
        "final_url": None,
        "error": None,
        "method_used": None,
        "response_time": None,
        "depth": None,
        "https": None,
        "internal": None,
        "status_category": None,
    }

    try:
        # HEAD first
        # Catch the time

        start = time.time()
        r = requests.head(
            url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True
        )
        response_time = time.time() - start

        result["response_time"] = round(response_time, 2)
        result["method_used"] = "HEAD"
        result["status_code"] = r.status_code
        result["final_url"] = r.url
        result["redirected"] = r.url != url

        if 200 <= r.status_code < 400:
            result["ok"] = True
            return result

        # Try GET if 405 or >=400
        if r.status_code >= 400 or r.status_code == 405:
            g = requests.get(
                url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True
            )
            result["method_used"] = "GET"
            result["status_code"] = g.status_code
            result["final_url"] = g.url
            result["redirected"] = g.url != url
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
