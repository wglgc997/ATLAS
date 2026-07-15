from fastapi import APIRouter

from src.schemas.scan import ScanResponse, ScanRequest
from src.services.scan_service import scan_page

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("", response_model=ScanResponse)
def run_scan(request: ScanRequest) -> ScanResponse:
    """Execute the complete scan of a page
    The endpoint receives a page URL from the frontend,
    extracts all links, validates them and returns a
    summarized report.
    """

    return scan_page(
        page_url=str(request.url),
        timeout=request.timeout,
        max_workers=request.max_workers,
        include_assets=request.include_assets,
        include_external=request.include_external,
    )
