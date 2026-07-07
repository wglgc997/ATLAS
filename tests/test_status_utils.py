from src.utils.status_utils import status_category

def test_status_category_success():
    """2xx status code as success"""

    assert status_category(200) == "success"


def test_status_category_redirect():
    """3xx status code as redirected"""

    assert status_category(300) == "redirected"


def test_status_category_client_error():
    """4xx status code as client error"""

    assert status_category(400) == "client_error"


def test_status_category_server_error():
    """5xx status code as server error"""

    assert status_category(500) == "server_error"

def test_status_category_unknown_when_none():
    """Should classify missing status code as unknown."""
    assert status_category(None) == "unknown"