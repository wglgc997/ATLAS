from src.checker.link_checker import check_link
from src.config.settings import HTTP_TIMEOUT
from src.schemas.link import ExtractedLink, InteractionStatus
from src.schemas.scan import LinkResult, LinkStatus
from src.services.link_normalizer import get_invalid_link_reason, get_raw_link_value


def normalize_link_status(status: object) -> LinkStatus:
    if status == "Good":
        return LinkStatus.GOOD

    try:
        return LinkStatus(status)
    except ValueError:
        return LinkStatus.UNKNOWN_ERROR


def build_invalid_link_result(
        link: ExtractedLink,
        page_url: str,
        reason: str,
) -> LinkResult:
    raw_link_value = get_raw_link_value(link)
    display_url = raw_link_value if isinstance(raw_link_value, str) else ""

    return LinkResult(
        url=display_url,
        final_url=None,
        http_status=None,
        status=LinkStatus.INVALID_LINK,
        redirect_chain=[],
        response_time_ms=0,
        error_message=reason,
        error_description=reason,
        technical_details=None,
        source_page=page_url,
        link_text=link.link_text,
        link_type=link.link_type,
        source_attribute=link.source_attribute or "href",
        source_location=link.source_location,
    )


def build_interaction_result(
        link: ExtractedLink,
        page_url: str,
) -> LinkResult:
    raw_link_value = get_raw_link_value(link)
    display_url = raw_link_value if isinstance(raw_link_value, str) else ""
    detail = link.interaction_detail or link.interaction_error

    status = (
        LinkStatus.INTERACTIVE_ELEMENT
        if link.interaction_status == InteractionStatus.INTERACTIVE
        else LinkStatus.INTERACTION_ERROR
    )

    return LinkResult(
        url=display_url,
        final_url=None,
        http_status=None,
        status=status,
        redirect_chain=[],
        response_time_ms=0,
        error_message=None if status == LinkStatus.INTERACTIVE_ELEMENT else detail,
        error_description=detail,
        technical_details=detail,
        source_page=page_url,
        link_text=link.link_text,
        link_type=link.link_type,
        source_attribute=link.source_attribute or "href",
        source_location=link.source_location,
    )


def build_link_result(
        link: ExtractedLink,
        page_url: str,
        timeout: int = HTTP_TIMEOUT,
) -> LinkResult | None:
    link_url = link.url

    if link.interaction_status in {
        InteractionStatus.INTERACTIVE,
        InteractionStatus.ERROR,
    }:
        return build_interaction_result(
            link=link,
            page_url=page_url,
        )

    invalid_reason = link.invalid_reason or get_invalid_link_reason(
        get_raw_link_value(link)
    )

    if invalid_reason:
        return build_invalid_link_result(
            link=link,
            page_url=page_url,
            reason=invalid_reason,
        )

    if not link_url:
        return build_invalid_link_result(
            link=link,
            page_url=page_url,
            reason="Missing href attribute.",
        )

    checked_link = check_link(
        url=link_url,
        timeout=timeout,
    )

    status = normalize_link_status(checked_link.get("status"))

    return LinkResult(
        url=link_url,
        final_url=checked_link.get("final_url"),
        http_status=checked_link.get("http_status"),
        status=status,
        redirect_chain=checked_link.get("redirect_chain") or [],
        response_time_ms=checked_link.get("response_time_ms"),
        error_message=checked_link.get("error_message"),
        error_description=checked_link.get("error_description"),
        technical_details=checked_link.get("technical_details"),
        source_page=page_url,
        link_text=link.link_text,
        link_type=link.link_type,
        source_attribute=link.source_attribute,
        source_location=link.source_location,
    )
