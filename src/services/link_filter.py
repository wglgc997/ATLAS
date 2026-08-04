from src.services.link_normalizer import (
    get_invalid_link_reason,
    get_raw_link_value,
    is_ignored_domain,
    is_same_domain,
    normalize_label,
    normalize_link_url,
)
from src.schemas.link import ExtractedLink, InteractionStatus

IGNORED_UI_LINK_TEXTS = {
    "account",
    "au/en",
    "cart",
    "my account",
    "order status",
    "profile settings",
    "sign in",
}
TECHNICAL_LINK_TYPES = {"resource", "script", "image", "iframe"}


def should_ignore_page_chrome_link(link: ExtractedLink) -> bool:
    if link.ignored:
        return True

    label = normalize_label(link.link_text)
    location = normalize_label(link.source_location)
    raw_link_value = get_raw_link_value(link)
    invalid_reason = get_invalid_link_reason(raw_link_value)

    if label in IGNORED_UI_LINK_TEXTS:
        return True

    if invalid_reason and "without visible text" in location:
        return True

    return False


def filter_links(
        links: list[ExtractedLink],
        page_url: str,
        include_assets: bool,
        include_external: bool,
) -> list[ExtractedLink]:

    filtered_links: list[ExtractedLink] = []
    seen_urls: set[str] = set()

    for link in links:
        if should_ignore_page_chrome_link(link):
            continue

        if not include_assets and link.link_type in TECHNICAL_LINK_TYPES:
            continue

        raw_link_value = get_raw_link_value(link)
        invalid_reason = get_invalid_link_reason(raw_link_value)

        if link.interaction_status == InteractionStatus.NAVIGATED:
            link_url = normalize_link_url(link.url, page_url)

            if not link_url:
                filtered_links.append(
                    link.model_copy(
                        update={
                            "interaction_status": InteractionStatus.ERROR,
                            "interaction_error": "Click navigated to a non-HTTP URL.",
                        }
                    )
                )

                continue

            invalid_reason = None
            link = link.model_copy(update={"url": link_url})
        elif link.interaction_status in {
            InteractionStatus.INTERACTIVE,
            InteractionStatus.ERROR,
        }:
            dedupe_key = "|".join(
                [
                    str(raw_link_value),
                    str(link.source_attribute),
                    str(link.source_location),
                    str(link.interaction_status),
                ]
            )

            if dedupe_key in seen_urls:
                continue

            seen_urls.add(dedupe_key)
            filtered_links.append(link)

            continue

        if invalid_reason:
            dedupe_key = "|".join(
                [
                    str(raw_link_value),
                    str(link.source_attribute),
                    str(link.source_location),
                ]
            )

            if dedupe_key in seen_urls:
                continue

            seen_urls.add(dedupe_key)

            filtered_links.append(
                link.model_copy(
                    update={
                        "url": raw_link_value if isinstance(raw_link_value, str) else "",
                        "invalid_reason": invalid_reason,
                    }
                )
            )

            continue

        link_url = normalize_link_url(link.url, page_url)

        if not link_url:
            continue

        if is_ignored_domain(link_url):
            continue

        if not include_external and not is_same_domain(link_url, page_url):
            continue

        if link_url in seen_urls:
            continue

        seen_urls.add(link_url)

        filtered_links.append(link.model_copy(update={"url": link_url}))

    return filtered_links
