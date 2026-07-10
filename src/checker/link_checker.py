import time
import requests
from requests import exceptions

from src.config.settings import VERIFY_SSL


def classify_status(http_status: int | None, was_redirected: bool) -> str:
    """Classify the link result"""

    if http_status is None:
        return "Broken"

    if was_redirected:
        return "Redirected"

    if 200 <= http_status <= 299:
        return "Good"

    if 300 <= http_status <= 399:
        return "Redirected"

    if 400 <= http_status <= 599:
        return "Broken"

    return "Broken"


def check_link(url: str, timeout: int = 10) -> dict:
    """
    Verify a URL and return a pattern result.

    This DON'T access any sharepoint or
    salve a CSV file.
    """

    start_time = time.perf_counter()

    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            verify=VERIFY_SSL,
            headers={
                "User-Agent": "Mozilla/5.0 LinkChecker/1.0"
            },
        )

        response_time_ms = round((time.perf_counter() - start_time) * 1000)

        was_redirected = len(response.history) > 0

        status = classify_status(
            http_status=response.status_code,
            was_redirected=was_redirected,
        )

        return {
            "url": url,
            "final_url": response.url,
            "http_status": response.status_code,
            "status": status,
            "response_time_ms": response_time_ms,
            "error_message": None,
        }

    except (
        exceptions.ConnectionError,
        exceptions.HTTPError,
        exceptions.ReadTimeout,
        exceptions.Timeout,
    ) as error:
        response_time_ms = round((time.perf_counter() - start_time) * 1000)

        return {
            "url": url,
            "final_url": None,
            "http_status": None,
            "status": "Broken",
            "response_time_ms": response_time_ms,
            "error_message": str(error),
        }

    except (
        exceptions.InvalidSchema,
        exceptions.InvalidURL,
        exceptions.MissingSchema,
        exceptions.TooManyRedirects,
        requests.RequestException,
    ) as error:
        response_time_ms = round((time.perf_counter() - start_time) * 1000)

        return {
            "url": url,
            "final_url": None,
            "http_status": None,
            "status": "Error",
            "response_time_ms": response_time_ms,
            "error_message": str(error),
        }

