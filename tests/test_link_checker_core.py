from src.checker.link_checker import classify_status
from src.crawler.extractor import extract_links_from_html
from src.schemas.link import ExtractedLink, LinkType
from src.schemas.scan import HealthState, LinkResult, LinkStatusGroup, ScanResponse
from src.services import link_result_builder, scan_history, scan_service
from src.services.link_filter import filter_links
from src.services.link_result_builder import build_link_result
from src.services.scan_summary import build_scan_response


def link(**values) -> ExtractedLink:
    return ExtractedLink.model_validate(values)


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

    assert [item.model_dump() for item in links] == [
        {
            "url": "https://example.com/about",
            "raw_url": "/about#team",
            "link_text": "About us",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: About us",
            "ignored": False,
            "element_index": None,
            "interaction_status": None,
            "interaction_detail": None,
            "interaction_error": None,
            "invalid_reason": None,
        },
        {
            "url": "mailto:test@example.com",
            "raw_url": "mailto:test@example.com",
            "link_text": "Email",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Email",
            "ignored": False,
            "element_index": None,
            "interaction_status": None,
            "interaction_detail": None,
            "interaction_error": None,
            "invalid_reason": None,
        },
        {
            "url": "https://example.com/static/app.css",
            "raw_url": "/static/app.css",
            "link_text": None,
            "link_type": "resource",
            "source_attribute": "href",
            "source_location": "Stylesheet: app.css",
            "ignored": False,
            "element_index": None,
            "interaction_status": None,
            "interaction_detail": None,
            "interaction_error": None,
            "invalid_reason": None,
        },
        {
            "url": "https://example.com/static/app.js",
            "raw_url": "/static/app.js",
            "link_text": None,
            "link_type": "script",
            "source_attribute": "src",
            "source_location": "Script: app.js",
            "ignored": False,
            "element_index": None,
            "interaction_status": None,
            "interaction_detail": None,
            "interaction_error": None,
            "invalid_reason": None,
        },
        {
            "url": "https://example.com/path/images/logo.png",
            "raw_url": "images/logo.png",
            "link_text": None,
            "link_type": "image",
            "source_attribute": "src",
            "source_location": "Image: Logo",
            "ignored": False,
            "element_index": None,
            "interaction_status": None,
            "interaction_detail": None,
            "interaction_error": None,
            "invalid_reason": None,
        },
        {
            "url": "https://example.org/embed",
            "raw_url": "https://example.org/embed",
            "link_text": None,
            "link_type": "iframe",
            "source_attribute": "src",
            "source_location": "Iframe: embed",
            "ignored": False,
            "element_index": None,
            "interaction_status": None,
            "interaction_detail": None,
            "interaction_error": None,
            "invalid_reason": None,
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


def test_link_result_derives_status_group_for_legacy_data() -> None:
    result = LinkResult.model_validate(
        {
            "url": "https://example.com/private",
            "status": "Forbidden",
            "source_page": "https://example.com",
        }
    )

    assert result.status_group == LinkStatusGroup.BROKEN


def test_build_scan_response_includes_ui_summary() -> None:
    results = [
        LinkResult(
            url="https://example.com/ok",
            status="Valid",
            source_page="https://example.com",
        ),
        LinkResult(
            url="https://example.com/redirect",
            status="Redirected",
            source_page="https://example.com",
        ),
        LinkResult(
            url="https://example.com/missing",
            status="Broken",
            source_page="https://example.com",
        ),
    ]

    scan = build_scan_response(
        source_page="https://example.com",
        results=results,
    )

    assert scan.summary is not None
    assert scan.summary.total_links == 3
    assert scan.summary.healthy_count == 2
    assert scan.summary.needs_action_count == 1
    assert scan.summary.health_score == 67
    assert scan.summary.health_state == HealthState.DANGER
    assert scan.summary.health_message == "1 link needs review."
    assert scan.summary.summary_message == (
        "Scan completed. 1 of 3 links needs attention."
    )


def test_build_scan_response_uses_singular_summary_messages() -> None:
    scan = build_scan_response(
        source_page="https://example.com",
        results=[
            LinkResult(
                url="https://example.com/ok",
                status="Valid",
                source_page="https://example.com",
            ),
        ],
    )

    assert scan.summary is not None
    assert scan.summary.health_message == "No immediate fixes required."
    assert scan.summary.summary_message == (
        "Scan completed. All 1 link is valid."
    )


def test_build_scan_response_uses_singular_redirect_message() -> None:
    scan = build_scan_response(
        source_page="https://example.com",
        results=[
            LinkResult(
                url="https://example.com/redirect",
                status="Redirected",
                source_page="https://example.com",
            ),
        ],
    )

    assert scan.summary is not None
    assert scan.summary.summary_message == (
        "Scan completed. No broken links found; 1 redirect was detected."
    )


def test_build_scan_response_summarizes_empty_scan() -> None:
    scan = build_scan_response(
        source_page="https://example.com",
        results=[],
    )

    assert scan.summary is not None
    assert scan.summary.health_score == 0
    assert scan.summary.health_state == HealthState.DANGER
    assert scan.summary.health_message == "No immediate fixes required."
    assert scan.summary.summary_message == "No links were found in this scan."


def test_filter_links_normalizes_urls_and_skips_non_navigable_links() -> None:
    links = [
        link(url="/about#team", link_type=LinkType.ANCHOR),
        link(url="https://example.com/about", link_type=LinkType.ANCHOR),
        link(url="#content", link_type=LinkType.ANCHOR),
        link(url="mailto:test@example.com", link_type=LinkType.ANCHOR),
        link(url="tel:+5511999999999", link_type=LinkType.ANCHOR),
        link(url="javascript:void(0)", link_type=LinkType.ANCHOR),
        link(url="https://example.com/logo.png", link_type=LinkType.IMAGE),
        link(url="https://other.example/page", link_type=LinkType.ANCHOR),
    ]

    filtered_links = filter_links(
        links=links,
        page_url="https://example.com/path/page",
        include_assets=False,
        include_external=False,
    )

    assert [
        item.model_dump(exclude_none=True, exclude_defaults=True)
        for item in filtered_links
    ] == [
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
        link(**{
            "url": "",
            "raw_url": None,
            "link_text": "Sign In",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Sign In",
        }),
        link(**{
            "url": "",
            "raw_url": None,
            "link_text": "AU/EN",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: AU/EN",
        }),
        link(**{
            "url": "",
            "raw_url": None,
            "link_text": "Cart",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Cart",
        }),
        link(**{
            "url": "javascript:;",
            "raw_url": "javascript:;",
            "link_text": None,
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: without visible text",
        }),
        link(**{
            "url": "",
            "raw_url": None,
            "link_text": "Dell's Privacy Policy",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Dell's Privacy Policy",
        }),
    ]

    filtered_links = filter_links(
        links=links,
        page_url="https://example.com/path/page",
        include_assets=False,
        include_external=True,
    )

    assert [
        item.model_dump(exclude_none=True, exclude_defaults=True)
        for item in filtered_links
    ] == [
        {
            "url": "",
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
            link(**{
                "url": "https://example.com/ok",
                "link_text": "OK",
                "link_type": "anchor",
                "source_attribute": "href",
                "source_location": "Text link: OK",
            }),
            link(**{
                "url": "https://example.com/redirect",
                "link_text": "Redirect",
                "link_type": "anchor",
                "source_attribute": "href",
                "source_location": "Text link: Redirect",
            }),
            link(**{
                "url": "https://example.com/broken",
                "link_text": "Broken",
                "link_type": "anchor",
                "source_attribute": "href",
                "source_location": "CTA: Broken",
            }),
            link(**{
                "url": "invalid://url",
                "link_text": "Invalid",
                "link_type": "anchor",
                "source_attribute": "href",
                "source_location": "Text link: Invalid",
            }),
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
    monkeypatch.setattr(link_result_builder, "check_link", fake_check_link)

    scan = scan_service.scan_page("https://example.com", timeout=5)

    assert scan.total_links == 4
    assert scan.good == 1
    assert scan.redirected == 1
    assert scan.broken == 2
    assert scan.error == 0
    assert scan.results[0].link_text == "OK"
    assert scan.results[0].status_group == "good"
    assert scan.results[1].status_group == "redirected"
    assert scan.results[2].status_group == "broken"
    assert scan.results[3].status_group == "broken"
    assert scan.summary is not None
    assert scan.summary.needs_action_count == 2
    assert scan.summary.health_score == 50
    assert scan.results[2].source_location == "CTA: Broken"
    assert scan.results[3].status == "Invalid Link"
    assert classify_status(301, False) == "Redirect Loop"
    assert classify_status(302, False) == "Redirect Loop"
    assert classify_status(308, False) == "Redirect Loop"


def test_interactive_suspicious_link_is_not_broken() -> None:
    result = build_link_result(
        link=link(**{
            "url": "",
            "raw_url": None,
            "link_text": "Cart",
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: Cart",
            "interaction_status": "interactive",
            "interaction_detail": "Click changed visible page state.",
        }),
        page_url="https://example.com",
    )

    assert result is not None
    assert result.status == "Interactive Element"
    assert result.error_message is None


def test_suspicious_link_without_effect_is_interaction_error() -> None:
    result = build_link_result(
        link=link(**{
            "url": "javascript:;",
            "raw_url": "javascript:;",
            "link_text": None,
            "link_type": "anchor",
            "source_attribute": "href",
            "source_location": "Text link: without visible text",
            "interaction_status": "error",
            "interaction_error": "Click did not produce navigation or a detectable interaction.",
        }),
        page_url="https://example.com",
    )

    assert result is not None
    assert result.status == "Interaction Error"
    assert result.error_message == "Click did not produce navigation or a detectable interaction."


def test_save_scan_to_history_replaces_closed_temp_file(monkeypatch, tmp_path) -> None:
    history_file = tmp_path / "scan_history.json"
    monkeypatch.setattr(scan_history, "HISTORY_FILE", history_file)

    scan = ScanResponse(
        source_page="https://example.com",
        total_links=0,
        good=0,
        redirected=0,
        broken=0,
        error=0,
        results=[],
    )

    item = scan_history.save_scan_to_history(scan)

    assert history_file.exists()
    assert scan_history.load_scan_history()[0]["id"] == item["id"]
    assert list(tmp_path.glob("*.tmp")) == []


def test_get_scan_from_history_checks_all_items(monkeypatch, tmp_path) -> None:
    history_file = tmp_path / "scan_history.json"
    history_file.write_text(
        '[{"id": "first", "source_page": "https://a.example"}, '
        '{"id": "second", "source_page": "https://b.example"}]',
        encoding="utf-8",
    )
    monkeypatch.setattr(scan_history, "HISTORY_FILE", history_file)

    assert scan_history.get_scan_from_history("second")["source_page"] == "https://b.example"
    assert scan_history.get_scan_from_history("missing") is None
