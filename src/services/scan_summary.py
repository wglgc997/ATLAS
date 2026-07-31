from src.schemas.scan import LinkResult, LinkStatus, ScanResponse

def build_scan_response(source_page: str, results: list[LinkResult]) -> ScanResponse:
    error_statuses = {
        LinkStatus.SSL_ERROR,
        LinkStatus.TIMEOUT,
        LinkStatus.CONNECTION_ERROR,
        LinkStatus.DNS_ERROR,
        LinkStatus.UNKNOWN_ERROR
    }

    broken_statuses = {
        LinkStatus.BROKEN,
        LinkStatus.UNAUTHORIZED,
        LinkStatus.FORBIDDEN,
        LinkStatus.GONE,
        LinkStatus.SERVER_ERROR,
        LinkStatus.INVALID_LINK,
        LinkStatus.INTERACTION_ERROR,
        LinkStatus.REDIRECT_LOOP
    }

    good = sum(
        result.status in {LinkStatus.GOOD, LinkStatus.INTERACTIVE_ELEMENT}
        for result in results
    )

    redirected = sum(result.status == LinkStatus.REDIRECTED for result in results)
    broken = sum(result.status in broken_statuses for result in results)
    error = sum(result.status in error_statuses for result in results)

    return ScanResponse(
        source_page=source_page,
        total_links=len(results),
        good=good,
        redirected=redirected,
        broken=broken,
        error=error,
        results=results,

    )
