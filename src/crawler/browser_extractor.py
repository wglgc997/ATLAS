from urllib.parse import urlparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from src.utils.runtime_paths import find_chromium_executable
from src.config.settings import (
    PLAYWRIGHT_INTERACTION_TIMEOUT,
    PLAYWRIGHT_TIMEOUT,
    WAIT_UNTIL,
)

SUSPICIOUS_SCHEMES = {"javascript", "mailto", "tel", "data"}
ANCHOR_SELECTOR = "a"


def is_suspicious_anchor(link: dict) -> bool:
    raw_url = link.get("raw_url")

    if raw_url is None:
        return True

    if not isinstance(raw_url, str):
        return True

    href = raw_url.strip()

    if not href or href == "#":
        return True

    scheme = urlparse(href).scheme.lower()

    return scheme in SUSPICIOUS_SCHEMES


def get_interaction_state(page) -> dict:
    return page.evaluate(
        """
        () => ({
            url: window.location.href,
            dialogCount: Array.from(document.querySelectorAll(
                '[role="dialog"], dialog, [aria-modal="true"], .modal'
            )).filter(element => {
                const style = window.getComputedStyle(element);
                const rect = element.getBoundingClientRect();

                return (
                    style.display !== "none" &&
                    style.visibility !== "hidden" &&
                    rect.width > 0 &&
                    rect.height > 0
                );
            }).length,
            expandedCount: Array.from(document.querySelectorAll(
                '[aria-expanded="true"]'
            )).length,
            bodyTextLength: document.body?.innerText?.length || 0,
            htmlLength: document.documentElement?.outerHTML?.length || 0
        })
        """
    )


def interaction_changed(before_state: dict, after_state: dict) -> bool:
    return (
        before_state.get("url") != after_state.get("url")
        or after_state.get("dialogCount", 0) > before_state.get("dialogCount", 0)
        or after_state.get("expandedCount", 0) > before_state.get("expandedCount", 0)
        or abs(after_state.get("bodyTextLength", 0) - before_state.get("bodyTextLength", 0)) > 40
        or abs(after_state.get("htmlLength", 0) - before_state.get("htmlLength", 0)) > 120
    )


def validate_suspicious_interactions(page, page_url: str, links: list[dict]) -> None:
    interaction_timeout_ms = PLAYWRIGHT_INTERACTION_TIMEOUT * 1000

    for link in links:
        if link.get("ignored"):
            continue

        if not is_suspicious_anchor(link):
            continue

        element_index = link.get("element_index")

        if not isinstance(element_index, int):
            link["interaction_status"] = "error"
            link["interaction_error"] = "Unable to locate the element for interaction validation."

            continue

        try:
            page.goto(
                page_url,
                wait_until=WAIT_UNTIL,
                timeout=PLAYWRIGHT_TIMEOUT * 1000,
            )

            locator = page.locator(ANCHOR_SELECTOR).nth(element_index)

            before_pages = len(page.context.pages)
            before_state = get_interaction_state(page)

            locator.click(
                timeout=interaction_timeout_ms,
                no_wait_after=True,
            )

            page.wait_for_timeout(interaction_timeout_ms)

            after_state = get_interaction_state(page)

            if len(page.context.pages) > before_pages:
                link["interaction_status"] = "interactive"
                link["interaction_detail"] = "Click opened a new page or popup."
            elif before_state.get("url") != after_state.get("url"):
                link["interaction_status"] = "navigated"
                link["url"] = after_state.get("url")
                link["interaction_detail"] = "Click changed the current page URL."
            elif interaction_changed(before_state, after_state):
                link["interaction_status"] = "interactive"
                link["interaction_detail"] = "Click changed visible page state."
            else:
                link["interaction_status"] = "error"
                link["interaction_error"] = "Click did not produce navigation or a detectable interaction."

        except (PlaywrightTimeoutError, PlaywrightError) as error:
            link["interaction_status"] = "error"
            link["interaction_error"] = str(error)


def extract_links_with_browser(page_url: str) -> list[dict]:
    """
    Render a web page and extract its links using bundled Chromium.

    Args:
        page_url: URL of the page that should be rendered.

    Returns:
        A list containing the links found on the rendered page.
    """
    chromium_executable = find_chromium_executable()

    print(f"Using bundled Chromium: {chromium_executable}")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path=str(chromium_executable),
        )

        try:
            page = browser.new_page()

            page.goto(
                page_url,
                wait_until=WAIT_UNTIL,
                timeout= PLAYWRIGHT_TIMEOUT * 1000,
            )

            page.wait_for_selector(
                "a",
                timeout= PLAYWRIGHT_TIMEOUT * 1000,
            )

            links = page.locator(ANCHOR_SELECTOR).evaluate_all(
                """
                elements => elements.map((element, index) => ({
                    element_index: index,
                    url: element.hasAttribute("href") ? element.href : null,
                    raw_url: element.getAttribute("href"),
                    link_text: element.innerText?.trim() || null,
                    link_type: "anchor",
                    source_attribute: "href",
                    ignored: Boolean(element.closest(
                        [
                            "header",
                            "footer",
                            "nav",
                            "[role='banner']",
                            "[role='contentinfo']",
                            "[role='navigation']",
                            "[aria-label*='navigation' i]",
                            "[aria-label*='breadcrumb' i]",
                            "[class*='header' i]",
                            "[class*='footer' i]",
                            "[class*='nav' i]",
                            "[class*='menu' i]",
                            "[class*='breadcrumb' i]",
                            "[class*='account' i]",
                            "[class*='cart' i]",
                            "[id*='header' i]",
                            "[id*='footer' i]",
                            "[id*='nav' i]",
                            "[id*='menu' i]",
                            "[id*='breadcrumb' i]",
                            "[id*='account' i]",
                            "[id*='cart' i]"
                        ].join(",")
                    )),
                    source_location: element.innerText?.trim()
                        ? `Text link: ${element.innerText.trim()}`
                        : "Text link: without visible text"
                }))
                """
            )

            validate_suspicious_interactions(page, page_url, links)

            return links

        finally:
            browser.close()
