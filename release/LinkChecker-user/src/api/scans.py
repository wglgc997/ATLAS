import json
from concurrent.futures import ThreadPoolExecutor
from collections.abc import Callable
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.schemas.scan import ScanBatchItem, ScanBatchResponse, ScanJobResponse, ScanResponse, ScanRequest
from src.services.scan_history import (
    clear_scan_history,
    get_scan_from_history,
    list_scan_history,
    save_scan_to_history,
)
from src.services.scan_service import scan_page
from src.services.scan_jobs import scan_jobs


router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("", response_model=ScanResponse | ScanBatchResponse)
def run_scan(request: ScanRequest) -> ScanResponse | ScanBatchResponse:
    """Execute the complete scan of a page
    The endpoint receives a page URL from the frontend,
    extracts all links, validates them and returns a
    summarized report.
    """

    return _run_scan(request)


def _run_scan(
    request: ScanRequest,
    progress_callback: Callable[[dict], None] | None = None,
) -> ScanResponse | ScanBatchResponse:
    urls = [str(request.url)]
    if request.url_2:
        urls.append(str(request.url_2))

    batch_id = str(uuid4())
    def scan_url(url: str) -> ScanBatchItem:
        try:
            scan = scan_page(
                page_url=url,
                timeout=request.timeout,
                max_workers=request.max_workers,
                include_assets=request.include_assets,
                include_external=request.include_external,
                progress_callback=(
                    lambda stage, total_links, checked_links: progress_callback({
                        "url": url,
                        "stage": stage,
                        "total_links": total_links,
                        "checked_links": checked_links,
                    })
                    if progress_callback else None
                ),
            )
            return ScanBatchItem(url=url, scan=scan)
        except Exception as error:
            return ScanBatchItem(url=url, error=str(error) or "Scan failed.")

    # Independent pages can render and validate concurrently. ``map`` keeps
    # URL 1 / URL 2 order stable for the response and tabs.
    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        outcomes = list(executor.map(scan_url, urls))

    # Persist serially so simultaneous scans cannot overwrite each other's
    # local history updates.
    for outcome in outcomes:
        if outcome.scan:
            save_scan_to_history(outcome.scan, batch_id=batch_id)

    # Keep the original response shape when only one URL is sent.
    if len(outcomes) == 1 and outcomes[0].scan:
        return outcomes[0].scan
    return ScanBatchResponse(batch_id=batch_id, scans=outcomes)


@router.post("/jobs", response_model=ScanJobResponse, status_code=202)
def create_scan_job(request: ScanRequest) -> ScanJobResponse:
    """Start a local scan and return immediately with a progress job ID."""
    return scan_jobs.create(request, _run_scan)


@router.get("/jobs/{job_id}", response_model=ScanJobResponse)
def get_scan_job(job_id: str) -> ScanJobResponse:
    job = scan_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Scan job not found or expired.")
    return job


@router.get("/jobs/{job_id}/events")
def scan_job_events(job_id: str) -> StreamingResponse:
    """Stream real scan progress to the local dashboard using SSE."""
    if scan_jobs.get(job_id) is None:
        raise HTTPException(status_code=404, detail="Scan job not found or expired.")

    def stream():
        revision = -1
        while True:
            job, revision = scan_jobs.wait_for_update(job_id, revision)
            if job is None:
                return
            payload = json.dumps(job.model_dump(mode="json"))
            yield f"data: {payload}\n\n"
            if job.status.value in {"completed", "failed"}:
                return

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@router.get("/history")
def get_history() -> list[dict]:
    return list_scan_history()


@router.delete("/history", status_code=204)
def clear_history() -> None:
    clear_scan_history()

@router.get("/history/{scan_id}", response_model=ScanResponse)
def get_history_scan(scan_id: str) -> ScanResponse:
    scan = get_scan_from_history(scan_id)

    if scan is None:
        raise HTTPException(status_code=404, detail="Scan history item not found.")

    return ScanResponse.model_validate(scan)
