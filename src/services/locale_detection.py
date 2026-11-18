import re
from urllib.parse import urlparse
import requests
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from src.crawler.browser_extractor import launch_browser
from src.config.settings import PLAYWRIGHT_TIMEOUT, WAIT_UNTIL

LOCALE_PATTERN = re.compile(r"(?<![a-z])([a-z]{2,3})[-_]([a-z]{2})(?![a-z])", re.IGNORECASE)
LANGUAGE_HINTS = {
    "en": {"learn", "more", "read", "download", "here", "about"},
    "pt": {"saiba", "mais", "leia", "aqui", "baixar", "conheça"},
    "es": {"más", "lea", "aquí", "descargar", "conozca"},
    "fr": {"plus", "lire", "ici", "télécharger", "découvrir", "savoir"},
    "sk": {"viac", "čítať", "stiahnuť", "tu"},
}


def extract_locale(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(str(url))
    for value in (parsed.path, parsed.netloc):
        match = LOCALE_PATTERN.search(value)
        if match:
            return f"{match.group(1).lower()}-{match.group(2).upper()}"
    return None


def locales_match(source: str | None, target: str | None) -> bool:
    if not source or not target:
        return False
    return source.split("-", 1)[0].lower() == target.split("-", 1)[0].lower()


def build_locale_issue(source_url: str, target_url: str, link_text: str | None) -> dict | None:
    source_locale = extract_locale(source_url)
    target_locale = extract_locale(target_url)
    if not source_locale or not target_locale or locales_match(source_locale, target_locale):
        return None
    target_path = target_url.lower().split("?", 1)[0]
    return {
        "url": target_url,
        "anchor_text": link_text,
        "source_locale": source_locale,
        "target_locale": target_locale,
        "target_type": "pdf" if target_path.endswith(".pdf") else "page",
        "message": "The target locale differs from the source locale.",
    }


def detect_text_language(text: str | None) -> str | None:
    if not text:
        return None
    words = set(re.findall(r"[a-zÀ-ÿ]+", text.lower()))
    scores = {language: len(words & hints) for language, hints in LANGUAGE_HINTS.items()}
    language, score = max(scores.items(), key=lambda item: item[1])
    return language if score else None


def build_anchor_issue(
    source_locale: str | None,
    target_url: str,
    link_text: str | None,
) -> dict | None:
    anchor_language = detect_text_language(link_text)
    source_language = source_locale.split("-", 1)[0].lower() if source_locale else None
    target_locale = extract_locale(target_url)
    target_language = target_locale.split("-", 1)[0].lower() if target_locale else None
    if not anchor_language or not source_language:
        return None
    if anchor_language == source_language and (not target_language or target_language == source_language):
        return None
    return {
        "url": target_url,
        "anchor_text": link_text,
        "source_locale": source_locale,
        "anchor_locale": anchor_language,
        "target_locale": target_locale,
        "target_type": "pdf" if target_url.lower().split("?", 1)[0].endswith(".pdf") else "page",
        "reason": "anchor_and_target" if target_language and target_language != source_language else "anchor_text",
        "message": "The link text or destination uses a different language from the source page.",
    }


def detect_target_locale(url: str, timeout: int = 20) -> str | None:
    """Read a destination page's declared locale without downloading binaries."""
    clean_url = url.lower().split("?", 1)[0]
    if clean_url.endswith(".pdf"):
        return extract_locale(url)
    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 LinkChecker/1.0"},
            stream=True,
        )
        content_type = response.headers.get("content-type", "").lower()
        if "html" not in content_type:
            response.close()
            return extract_locale(response.url) if "pdf" in content_type else None
        body = next(response.iter_content(chunk_size=262144), b"")
        response.close()
        text = body.decode(response.encoding or "utf-8", errors="ignore")
        lang_match = re.search(r"<html[^>]+\blang=['\"]?([^\s>'\"]+)", text, re.I)
        if lang_match:
            return lang_match.group(1)
        content_language = re.search(r"<meta[^>]+http-equiv=['\"]content-language['\"][^>]+content=['\"]([^'\"]+)", text, re.I)
        if content_language:
            return content_language.group(1).split(",")[0].strip()
        visible_text = re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<[^>]+>", " ", text, flags=re.I | re.S)
        detected_language = detect_text_language(visible_text)
        if detected_language:
            return detected_language
    except requests.RequestException:
        pass

    try:
        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            try:
                page = browser.new_page()
                page.goto(url, wait_until=WAIT_UNTIL, timeout=min(timeout, PLAYWRIGHT_TIMEOUT) * 1000)
                locale = page.locator("html").get_attribute("lang")
                if locale:
                    return locale
                detected_language = detect_text_language(page.locator("body").inner_text())
                return detected_language or extract_locale(page.url)
            finally:
                browser.close()
    except (PlaywrightError, Exception):
        return extract_locale(url)
