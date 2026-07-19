from src.checker.link_checker import classify_status
from src.crawler.extractor import extract_links_from_html
from src.services import scan_service


def test_extract_links_from_html_resolves_relevant_links() -> None:
    html = """
    <html>
        <head>
            <link rel="stylesheet" href="/static/app.css">
            <script src="/static/app.js"></script>
        </head>
        <body>
            <a href="/about#team">About us</a>
            <a href="mailto:test@example.com">Email</a>
            <img src="images/logo.png" alt="Logo">
            <iframe src="https://example.org/embed"></iframe>
        </body>
    </html>
    """

    links = extract_links_from_html(html, "https://example.com/path/page")

    assert links == [
        {
            "url": "https://example.com/about",
            "link_text": "About us",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: About us",
        },
        {
            "url": "https://example.com/static/app.css",
            "link_text": None,
            "link_type": "resource",
            "source_attribute": "href",
            "source_location": "Stylesheet: app.css",
        },
        {
            "url": "https://example.com/static/app.js",
            "link_text": None,
            "link_type": "script",
            "source_attribute": "src",
            "source_location": "Script: app.js",
        },
        {
            "url": "https://example.com/path/images/logo.png",
            "link_text": None,
            "link_type": "image",
            "source_attribute": "src",
            "source_location": "Image: Logo",
        },
        {
            "url": "https://example.org/embed",
            "link_text": None,
            "link_type": "iframe",
            "source_attribute": "src",
            "source_location": "Iframe: embed",
        },
    ]


def test_classify_status_categories() -> None:
    assert classify_status(200, False) == "Good"
    assert classify_status(204, False) == "Good"
    assert classify_status(200, True) == "Redirected"
    assert classify_status(301, False) == "Redirected"
    assert classify_status(404, False) == "Broken"
    assert classify_status(500, False) == "Broken"
    assert classify_status(None, False) == "Broken"


def test_filter_links_normalizes_urls_and_skips_non_navigable_links() -> None:
    links = [
        {"url": "/about#team", "link_type": "anchor"},
        {"url": "https://example.com/about", "link_type": "anchor"},
        {"url": "#content", "link_type": "anchor"},
        {"url": "mailto:test@example.com", "link_type": "anchor"},
        {"url": "tel:+5511999999999", "link_type": "anchor"},
        {"url": "javascript:void(0)", "link_type": "anchor"},
        {"url": "https://example.com/logo.png", "link_type": "image"},
        {"url": "https://other.example/page", "link_type": "anchor"},
    ]

    filtered_links = scan_service.filter_links(
        links=links,
        page_url="https://example.com/path/page",
        include_assets=False,
        include_external=False,
    )

    assert filtered_links == [
        {
            "url": "https://example.com/about",
            "link_type": "anchor",
        },
    ]


def test_scan_page_builds_summary(monkeypatch) -> None:
    def fake_extract_links(page_url: str):
        assert page_url == "https://example.com"

        return [
            {
                "url": "https://example.com/ok",
                "link_text": "OK",
                "link_type": "anchor",
                "source_attribute": "href",
                "source_location": "Text link: OK",
            },
            {
                "url": "https://example.com/redirect",
                "link_text": "Redirect",
                "link_type": "anchor",
                "source_attribute": "href",
                "source_location": "Text link: Redirect",
            },
            {
                "url": "https://example.com/broken",
                "link_text": "Broken",
                "link_type": "anchor",
                "source_attribute": "href",
                "source_location": "CTA: Broken",
            },
            {
                "url": "invalid://url",
                "link_text": "Invalid",
                "link_type": "anchor",
                "source_attribute": "href",
                "source_location": "Text link: Invalid",
            },
        ]

    def fake_check_link(url: str, timeout: int = 10):
        statuses = {
            "https://example.com/ok": ("https://example.com/ok", 200, "Good"),
            "https://example.com/redirect": (
                "https://example.org/final",
                200,
                "Redirected",
            ),
            "https://example.com/broken": (None, None, "Broken"),
            "invalid://url": (None, None, "Error"),
        }
        final_url, http_status, status = statuses[url]

        return {
            "url": url,
            "final_url": final_url,
            "http_status": http_status,
            "status": status,
            "response_time_ms": 12,
            "error_message": "bad url" if status == "Error" else None,
        }

    monkeypatch.setattr(scan_service, "extract_links_with_browser", fake_extract_links)
    monkeypatch.setattr(scan_service, "check_link", fake_check_link)

    scan = scan_service.scan_page("https://example.com", timeout=5)

    assert scan.total_links == 4
    assert scan.good == 1
    assert scan.redirected == 1
    assert scan.broken == 1
    assert scan.error == 1
    assert scan.results[0].link_text == "OK"
    assert scan.results[2].source_location == "CTA: Broken"
    assert classify_status(301, False) == "Redirected"
    assert classify_status(302, False) == "Redirected"
    assert classify_status(308, False) == "Redirected"
