def status_category(status):
    """Status code of the page"""
    if status is None:
        return "unknown"

    if 200 <= status < 300:
        return "success"

    if 300 <= status < 400:
        return "redirected"

    if 400 <= status < 500:
        return "client_error"

    if 500 <= status < 600:
        return "server_error"

    return "unknown"
