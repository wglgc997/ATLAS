from playwright.sync_api import sync_playwright

from src.utils.runtime_paths import find_chromium_executable
from src.config.settings import PLAYWRIGHT_TIMEOUT, WAIT_UNTIL


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
                "a[href]",
                timeout= PLAYWRIGHT_TIMEOUT * 1000,
            )

            links = page.locator(
                "a[href]:not(footer a):not(nav a):not([role='navigation'] a)"
            ).evaluate_all(
                """
                elements => elements.map(element => ({
                    url: element.href,
                    link_text: element.innerText?.trim() || null,
                    link_type: "anchor",
                    source_attribute: "href"
                }))
                """
            )

            return links

        finally:
            browser.close()