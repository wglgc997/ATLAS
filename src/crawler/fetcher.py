import requests

from src.config.settings import DEFAULT_HEADERS


def fetch_html(url: str, timeout: int = 15) -> str | None:
    """Download the HTML from page"""
    try:
        resp = requests.get(
            url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True
        )  # GET on http/https
        resp.raise_for_status()
        return resp.text
        # if an error occur, the HTML error is displayed

    except Exception:
        return None
        # any error return None
