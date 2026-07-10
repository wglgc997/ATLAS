from fastapi import APIRouter

from src.schemas.scan import ScanResponse, ScanRequest
from src.services.scan_service import scan_page

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("")
def run_scan(request: ScanRequest):
    """Execute the complete scan of a page"""


    result = scan_page(
        page_url=str(request.url),
        timeout=request.timeout,
    )

    return result