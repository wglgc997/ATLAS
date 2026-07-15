from urllib.parse import urldefrag, urljoin

from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag

SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")
LINK_SELECTORS = (
    ("a[href]", "href", "anchor"),
    ("link[href]", "href", "resource"),
    ("script[src]", "src", "script"),
    ("img[src]", "src", "image"),
    ("iframe[src]", "src", "iframe"),
)


def normalize_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    text = " ".join(value.split())

    return text or None


def get_attribute_text(tag: Tag, attributes: tuple[str, ...]) -> str | None:
    for attribute in attributes:
        value = normalize_text(tag.get(attribute))

        if value:
            return value

    return None


def get_file_name(value: object) -> str | None:
    text = normalize_text(value)

    if not text:
        return None

    return text.rstrip("/").split("/")[-1] or text


def get_nearest_section_label(tag: Tag) -> str | None:
    current: PageElement | None = tag.parent

    while isinstance(current, Tag):
        heading = current.find(["h1", "h2", "h3"], recursive=False)

        if isinstance(heading, Tag):
            heading_text = normalize_text(heading.get_text(" ", strip=True))

            if heading_text:
                return heading_text

        current = current.parent

    return None


def is_cta(tag: Tag) -> bool:
    values = [
        tag.get("id"),
        tag.get("role"),
        tag.get("class"),
    ]

    searchable = " ".join(
        " ".join(value) if isinstance(value, list) else str(value)
        for value in values
        if value
    ).lower()

    return any(
        keyword in searchable
        for keyword in ("button", "btn", "cta", "call-to-action")
    )


def format_location(kind: str, label: str, section_label: str | None) -> str:
    if section_label:
        return f"{kind}: {label} (section: {section_label})"

    return f"{kind}: {label}"


def build_source_location(tag: Tag, attribute: str, link_type: str) -> str:
    section_label = get_nearest_section_label(tag)

    if link_type == "image":
        label = (
            get_attribute_text(tag, ("alt", "aria-label", "title"))
            or get_file_name(tag.get(attribute))
            or "without label"
        )

        return format_location("Image", label, section_label)

    if link_type == "iframe":
        label = (
            get_attribute_text(tag, ("title", "aria-label", "name"))
            or get_file_name(tag.get(attribute))
            or "embedded content"
        )

        return format_location("Iframe", label, section_label)

    if link_type in ("resource", "script"):
        label = get_file_name(tag.get(attribute)) or "page resource"
        kind = "Stylesheet" if link_type == "resource" else "Script"

        return format_location(kind, label, section_label)

    image = tag.find("img")

    if isinstance(image, Tag):
        label = (
            get_attribute_text(image, ("alt", "aria-label", "title"))
            or get_attribute_text(tag, ("aria-label", "title"))
            or get_file_name(image.get("src"))
            or "without label"
        )

        return format_location("Image link", label, section_label)

    label = (
        normalize_text(tag.get_text(" ", strip=True))
        or get_attribute_text(tag, ("aria-label", "title"))
        or "without visible text"
    )

    kind = "CTA" if is_cta(tag) else "Text link"

    return format_location(kind, label, section_label)


def extract_links_from_html(html: str, base_url: str) -> list[dict[str, str | None]]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[dict[str, str | None]] = []
    seen_urls: set[tuple[str, str]] = set()

    for selector, attribute, link_type in LINK_SELECTORS:
        for tag in soup.select(selector):
            raw_value = tag.get(attribute)

            if not isinstance(raw_value, str):
                continue

            link_value = raw_value.strip()

            if not link_value:
                continue

            if link_value.lower().startswith(SKIP_SCHEMES):
                continue

            absolute_url, _fragment = urldefrag(urljoin(base_url, link_value))
            dedupe_key = (absolute_url, attribute)

            if dedupe_key in seen_urls:
                continue

            seen_urls.add(dedupe_key)

            links.append(
                {
                    "url": absolute_url,
                    "link_text": tag.get_text(" ", strip=True) or None,
                    "link_type": link_type,
                    "source_attribute": attribute,
                    "source_location": build_source_location(
                        tag,
                        attribute,
                        link_type,
                    ),
                }
            )

    return links
