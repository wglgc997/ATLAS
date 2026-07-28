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
            "raw_url": "/about#team",
            "link_text": "About us",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: About us",
        },
        {
            "url": "mailto:test@example.com",
            "raw_url": "mailto:test@example.com",
            "link_text": "Email",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Email",
        },
        {
            "url": "https://example.com/static/app.css",
            "raw_url": "/static/app.css",
            "link_text": None,
            "link_type": "resource",
            "source_attribute": "href",
            "source_location": "Stylesheet: app.css",
        },
        {
            "url": "https://example.com/static/app.js",
            "raw_url": "/static/app.js",
            "link_text": None,
            "link_type": "script",
            "source_attribute": "src",
            "source_location": "Script: app.js",
        },
        {
            "url": "https://example.com/path/images/logo.png",
            "raw_url": "images/logo.png",
            "link_text": None,
            "link_type": "image",
            "source_attribute": "src",
            "source_location": "Image: Logo",
        },
        {
            "url": "https://example.org/embed",
            "raw_url": "https://example.org/embed",
            "link_text": None,
            "link_type": "iframe",
            "source_attribute": "src",
            "source_location": "Iframe: embed",
        },
    ]


def test_classify_status_categories() -> None:
    assert classify_status(200, False) == "Valid"
    assert classify_status(204, False) == "Valid"
    assert classify_status(200, True) == "Redirected"
    assert classify_status(301, False) == "Redirect Loop"
    assert classify_status(302, True) == "Redirect Loop"
    assert classify_status(401, False) == "Unauthorized"
    assert classify_status(403, False) == "Forbidden"
    assert classify_status(404, False) == "Broken"
    assert classify_status(410, False) == "Gone"
    assert classify_status(500, False) == "Server Error"
    assert classify_status(None, False) == "Unknown Error"


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
        {
            "url": "mailto:test@example.com",
            "link_type": "anchor",
            "invalid_reason": "The href uses a non-navigable scheme: mailto:.",
        },
        {
            "url": "tel:+5511999999999",
            "link_type": "anchor",
            "invalid_reason": "The href uses a non-navigable scheme: tel:.",
        },
        {
            "url": "javascript:void(0)",
            "link_type": "anchor",
            "invalid_reason": "The href uses a non-navigable scheme: javascript:.",
        },
    ]


def test_filter_links_ignores_page_chrome_controls() -> None:
    links = [
        {
            "url": "",
            "raw_url": None,
            "link_text": "Sign In",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Sign In",
        },
        {
            "url": "",
            "raw_url": None,
            "link_text": "AU/EN",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: AU/EN",
        },
        {
            "url": "",
            "raw_url": None,
            "link_text": "Cart",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Cart",
        },
        {
            "url": "javascript:;",
            "raw_url": "javascript:;",
            "link_text": None,
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: without visible text",
        },
        {
            "url": "",
            "raw_url": None,
            "link_text": "Dell's Privacy Policy",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Dell's Privacy Policy",
        },
    ]

    filtered_links = scan_service.filter_links(
        links=links,
        page_url="https://example.com/path/page",
        include_assets=False,
        include_external=True,
    )

    assert filtered_links == [
        {
            "url": "",
            "raw_url": None,
            "link_text": "Dell's Privacy Policy",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Dell's Privacy Policy",
            "invalid_reason": "Missing href attribute.",
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
            "redirect_chain": [],
            "error_message": "bad url" if status == "Error" else None,
        }

    monkeypatch.setattr(scan_service, "extract_links_with_browser", fake_extract_links)
    monkeypatch.setattr(scan_service, "check_link", fake_check_link)

    scan = scan_service.scan_page("https://example.com", timeout=5)

    assert scan.total_links == 4
    assert scan.good == 1
    assert scan.redirected == 1
    assert scan.broken == 2
    assert scan.error == 0
    assert scan.results[0].link_text == "OK"
    assert scan.results[2].source_location == "CTA: Broken"
    assert scan.results[3].status == "Invalid Link"
    assert classify_status(301, False) == "Redirect Loop"
    assert classify_status(302, False) == "Redirect Loop"
    assert classify_status(308, False) == "Redirect Loop"


def test_interactive_suspicious_link_is_not_broken() -> None:
    result = scan_service.build_link_result(
        link={
            "url": "",
            "raw_url": None,
            "link_text": "Cart",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Cart",
            "interaction_status": "interactive",
            "interaction_detail": "Click changed visible page state.",
        },
        page_url="https://example.com",
    )

    assert result is not None
    assert result.status == "Interactive Element"
    assert result.error_message is None


def test_suspicious_link_without_effect_is_interaction_error() -> None:
    result = scan_service.build_link_result(
        link={
            "url": "javascript:;",
            "raw_url": "javascript:;",
            "link_text": None,
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: without visible text",
            "interaction_status": "error",
            "interaction_error": "Click did not produce navigation or a detectable interaction.",
        },
        page_url="https://example.com",
    )

    assert result is not None
    assert result.status == "Interaction Error"
    assert result.error_message == "Click did not produce navigation or a detectable interaction."
