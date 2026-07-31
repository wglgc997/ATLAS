from src.services.link_normalizer import (
    get_invalid_link_reason,
    get_raw_link_value,
    is_ignored_domain,
    is_same_domain,
    normalize_label,
    normalize_link_url
)

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

def should_ignore_page_chrome_link(link: dict) -> bool:
    if link.get("ignored"):
        return True

    label = normalize_label(link.get("link_text"))
    location = normalize_label(link.get("source_location"))
    raw_link_value = get_raw_link_value(link)
    invalid_reason = get_invalid_link_reason(raw_link_value)

    if label in IGNORED_UI_LINK_TEXTS:
        return True

    if invalid_reason and "without visible text" in location:
        return True

    return False


def filter_links(
        links: list[dict],
        page_url: str,
        include_assets: bool,
        include_external: bool,
) -> list[dict]:

    filtered_links = []
    seen_urls: set[str] = set()

    for link in links:
        if should_ignore_page_chrome_link(link):
            continue

        if not include_assets and link.get("link_type") in TECHNICAL_LINK_TYPES:
            continue

        raw_link_value = get_raw_link_value(link)
        invalid_reason = get_invalid_link_reason(raw_link_value)

        if link.get("interaction_status") == "navigated":
            link_url = normalize_link_url(link.get("url"), page_url)

            if not link_url:
                filtered_links.append(
                    {
                        **link,
                        "interaction_status": "error",
                        "interaction_error": "Click navigated to a non-HTTP URL.",
                    }
                )

                continue

            invalid_reason = None
            link = {
                **link,
                "url": link_url,
            }
        elif link.get("interaction_status") in {"interactive", "error"}:
            dedupe_key = "|".join(
                [
                    str(raw_link_value),
                    str(link.get("source_attribute")),
                    str(link.get("source_location")),
                    str(link.get("interaction_status")),
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
                    str(link.get("source_attribute")),
                    str(link.get("source_location")),
                ]
            )

            if dedupe_key in seen_urls:
                continue

            seen_urls.add(dedupe_key)

            filtered_links.append(
                {
                    **link,
                    "url": raw_link_value if isinstance(raw_link_value, str) else "",
                    "invalid_reason": invalid_reason,
                }
            )

            continue

        link_url = normalize_link_url(link.get("url"), page_url)

        if not link_url:
            continue

        if is_ignored_domain(link_url):
            continue

        if not include_external and not is_same_domain(link_url, page_url):
            continue

        if link_url in seen_urls:
            continue

        seen_urls.add(link_url)

        filtered_link = {
            **link,
            "url": link_url,
        }

        filtered_links.append(filtered_link)

    return filtered_links