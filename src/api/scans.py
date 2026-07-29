from fastapi import APIRouter, HTTPException

from src.schemas.scan import ScanResponse, ScanRequest
from src.services.scan_history import (
    get_scan_from_history,
    list_scan_history,
    save_scan_to_history,
)
from src.services.scan_service import scan_page


router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("", response_model=ScanResponse)
def run_scan(request: ScanRequest) -> ScanResponse:
    """Execute the complete scan of a page
    The endpoint receives a page URL from the frontend,
    extracts all links, validates them and returns a
    summarized report.
    """

    scan = scan_page(
        page_url=str(request.url),
        timeout=request.timeout,
        max_workers=request.max_workers,
        include_assets=request.include_assets,
        include_external=request.include_external,
    )

    save_scan_to_history(scan)
    return scan

@router.get("/history")
def get_history() -> list[dict]:
    return list_scan_history()

@router.get("/history/{scan_id}", response_model=ScanResponse)
def get_history_scan(scan_id: str) -> ScanResponse:
    scan = get_scan_from_history(scan_id)

    if scan is None:
        raise HTTPException(status_code=404, detail="Scan history item not found.")

    return ScanResponse.model_validate(scan)
