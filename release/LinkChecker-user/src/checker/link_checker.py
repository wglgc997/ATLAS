import time
import requests
from requests import exceptions

import socket

from src.schemas.scan import LinkStatus
from src.config.settings import HTTP_TIMEOUT, MAX_REDIRECTS, VERIFY_SSL, CA_BUNDLE_PATH, HTTP_RETRIES, HTTP_RETRY_BACKOFF



def classify_status(http_status: int | None, was_redirected: bool) -> LinkStatus:
    """Classify a link from the final HTTP status and redirect history."""

    if http_status is None:
        return LinkStatus.UNKNOWN_ERROR

    if 200 <= http_status <= 299:
        return LinkStatus.REDIRECTED if was_redirected else LinkStatus.GOOD

    if 300 <= http_status <= 399:
        return LinkStatus.REDIRECT_LOOP

    if http_status == 401:
        return LinkStatus.UNAUTHORIZED

    if http_status == 403:
        return LinkStatus.FORBIDDEN

    if http_status == 410:
        return LinkStatus.GONE

    if 400 <= http_status <= 499:
        return LinkStatus.BROKEN

    if 500 <= http_status <= 599:
        return LinkStatus.SERVER_ERROR

    return LinkStatus.UNKNOWN_ERROR


def build_redirect_chain(response: requests.Response) -> list[dict[str, int | str | None]]:
    responses = [*response.history, response]

    return [
        {
            "status_code": redirect_response.status_code,
            "url": redirect_response.url,
        }
        for redirect_response in responses
    ]

def is_dns_error(error: BaseException) -> bool:
    current_error: BaseException | None = error

    while current_error is not None:
        if isinstance(current_error, socket.gaierror):
            return True

        current_error = current_error.__cause__ or current_error.__context__

    error_message = str(error).lower()

    return (
        "name resolution" in error_message
        or "temporary failure in name resolution" in error_message
        or "failed to resolve" in error_message
        or "nodename nor servname provided" in error_message
        or "getaddrinfo failed" in error_message
    )

def get_ssl_verify_config() -> bool | str:
    if not VERIFY_SSL:
        return False

    if CA_BUNDLE_PATH:
        return CA_BUNDLE_PATH

    return True


def request_with_retry(
        session: requests.Session,
        method: str,
        url: str,
        timeout: int,
        headers: dict[str, str],
        verify: bool | str,
    ) -> requests.Response:
        last_error: requests.RequestException | None = None

        for attempt in range(HTTP_RETRIES + 1):
            try:
                response = session.request(
                    method,
                    url,
                    timeout=timeout,
                    allow_redirects=True,
                    verify=verify,
                    headers=headers,
                    stream=method.upper() == "GET",
                )

                return response

            except (
                exceptions.ConnectTimeout,
                exceptions.ReadTimeout,
                exceptions.Timeout,
                exceptions.ConnectionError,
            ) as error:
                last_error = error

                if attempt >= HTTP_RETRIES:
                    raise

                time.sleep(HTTP_RETRY_BACKOFF * (attempt + 1))

        raise last_error or exceptions.RequestException("Request failed")


def check_link(url: str, timeout: int = HTTP_TIMEOUT) -> dict:
    """
    Verify a URL and return a pattern result.

    This DON'T access any sharepoint or
    salve a CSV file.
    """

    start_time = time.perf_counter()

    ssl_verify = get_ssl_verify_config()

    try:
        session = requests.Session()
        session.max_redirects = MAX_REDIRECTS

        headers = {
            "User-Agent": "Mozilla/5.0 LinkChecker/1.0",
        }

        response = request_with_retry(
            session=session,
            method="HEAD",
            url=url,
            timeout=timeout,
            headers=headers,
            verify=ssl_verify,
        )

        if response.status_code in (403, 405):
            response = request_with_retry(
                session=session,
                method="GET",
                url=url,
                timeout=timeout,
                headers=headers,
                verify=ssl_verify,
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
            "status": status.value,
            "redirect_chain": build_redirect_chain(response),
            "response_time_ms": response_time_ms,
            "error_message": None,
            "error_description": None,
            "technical_details": None,
        }

    except exceptions.SSLError as error:
        response_time_ms = round((time.perf_counter() - start_time) * 1000)

        return build_error_result(
            url=url,
            status=LinkStatus.SSL_ERROR,
            error=error,
            response_time_ms=response_time_ms,
        )

    except (

            exceptions.ConnectTimeout,

            exceptions.ReadTimeout,

            exceptions.Timeout,

    ) as error:

        response_time_ms = round((time.perf_counter() - start_time) * 1000)

        return build_error_result(

            url=url,

            status=LinkStatus.TIMEOUT,

            error=error,

            response_time_ms=response_time_ms,

        )

    except exceptions.ConnectionError as error:
        response_time_ms = round((time.perf_counter() - start_time) * 1000)

        status = (
            LinkStatus.DNS_ERROR
            if is_dns_error(error)
            else LinkStatus.CONNECTION_ERROR
        )

        return build_error_result(
            url=url,
            status=status,
            error=error,
            response_time_ms=response_time_ms,
        )

    except exceptions.TooManyRedirects as error:
        response_time_ms = round((time.perf_counter() - start_time) * 1000)

        return build_error_result(
            url=url,
            status=LinkStatus.REDIRECT_LOOP,
            error=error,
            response_time_ms=response_time_ms,
        )

    except (
        exceptions.InvalidSchema,
        exceptions.InvalidURL,
        exceptions.MissingSchema,
    ) as error:
        response_time_ms = round((time.perf_counter() - start_time) * 1000)

        return build_error_result(
            url=url,
            status=LinkStatus.INVALID_LINK,
            error=error,
            response_time_ms=response_time_ms,
        )

    except (
        exceptions.HTTPError,
        requests.RequestException,
    ) as error:
        response_time_ms = round((time.perf_counter() - start_time) * 1000)

        return build_error_result(
            url=url,
            status=LinkStatus.UNKNOWN_ERROR,
            error=error,
            response_time_ms=response_time_ms,
        )


def get_error_description(status: LinkStatus) -> str:
    descriptions = {
        LinkStatus.SSL_ERROR: "Unable to validate the SSL certificate.",
        LinkStatus.TIMEOUT: "Request timed out.",
        LinkStatus.CONNECTION_ERROR: "Unable to connect to the server",
        LinkStatus.DNS_ERROR: "Unable to resolve the domain name",
        LinkStatus.REDIRECT_LOOP: "The link exceeded the redirect limit or ended on a redirect status.",
        LinkStatus.INVALID_LINK: "The HTML element does not contain a navigable link.",
        LinkStatus.UNKNOWN_ERROR: "The link could not be validated due to an unexpected error.",
    }

    return descriptions.get(
        status,
        "The link could not be validated.",
    )

def build_error_result(
    url: str,
    status: LinkStatus,
    error: BaseException,
    response_time_ms: int,
) -> dict:
    description = get_error_description(status)

    return {
        "url": url,
        "final_url": None,
        "http_status": None,
        "status": status.value,
        "redirect_chain": [],
        "response_time_ms": response_time_ms,
        "error_message": description,
        "error_description": description,
        "technical_details": str(error),
    }
