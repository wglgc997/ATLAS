from src.schemas.scan import HealthState, LinkResult, LinkStatusGroup, ScanResponse
from src.schemas.scan import ScanSummary


def pluralize(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural


def build_scan_response(source_page: str, results: list[LinkResult]) -> ScanResponse:
    good = sum(result.status_group == LinkStatusGroup.GOOD for result in results)
    redirected = sum(
        result.status_group == LinkStatusGroup.REDIRECTED
        for result in results
    )
    broken = sum(result.status_group == LinkStatusGroup.BROKEN for result in results)
    error = sum(result.status_group == LinkStatusGroup.ERROR for result in results)

    healthy_count = good + redirected
    needs_action_count = broken + error
    health_score = (
        round((healthy_count / len(results)) * 100)
        if results
        else 0
    )
    health_state = get_health_state(
        health_score=health_score,
        needs_action_count=needs_action_count,
    )

    summary = ScanSummary(
        total_links=len(results),
        good=good,
        redirected=redirected,
        broken=broken,
        error=error,
        healthy_count=healthy_count,
        needs_action_count=needs_action_count,
        health_score=health_score,
        health_state=health_state,
        health_message=get_health_message(needs_action_count),
        summary_message=get_summary_message(
            total_links=len(results),
            redirected=redirected,
            needs_action_count=needs_action_count,
        ),
    )

    return ScanResponse(
        source_page=source_page,
        total_links=len(results),
        good=good,
        redirected=redirected,
        broken=broken,
        error=error,
        summary=summary,
        results=results,
    )

def get_health_state(health_score: int, needs_action_count: int) -> HealthState:
    if needs_action_count == 0 and health_score >= 95:
        return HealthState.EXCELLENT
    if health_score >= 90:
        return HealthState.GOOD

    if health_score >= 70:
        return HealthState.WARNING

    return HealthState.DANGER

def get_summary_message(
        total_links: int,
        redirected: int,
        needs_action_count: int,
) -> str:
    if total_links == 0:
        return "No links were found in this scan."

    if needs_action_count == 0 and redirected == 0:
        link_word = pluralize(total_links, "link is", "links are")

        return f"Scan completed. All {total_links} {link_word} valid."

    if needs_action_count == 0:
        redirect_word = pluralize(redirected, "redirect was", "redirects were")

        return (
            "Scan completed. No broken links found; "
            f"{redirected} {redirect_word} detected."
        )

    link_word = pluralize(total_links, "link", "links")
    attention_verb = pluralize(needs_action_count, "needs", "need")

    return (
        f"Scan completed. {needs_action_count} of "
        f"{total_links} {link_word} {attention_verb} attention."
    )

def get_health_message(needs_action_count: int) -> str:
    if needs_action_count == 0:
        return "No immediate fixes required."

    link_word = pluralize(needs_action_count, "link", "links")
    review_verb = pluralize(needs_action_count, "needs", "need")

    return f"{needs_action_count} {link_word} {review_verb} review."
