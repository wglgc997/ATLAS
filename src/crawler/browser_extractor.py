from playwright.sync_api import sync_playwright

from src.crawler.extractor import extract_links_from_html


def extract_links_with_browser(page_url: str):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(
            page_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

        html = page.content()

        browser.close()

    return extract_links_from_html(html, page_url)