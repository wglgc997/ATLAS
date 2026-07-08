from pydantic import BaseModel
from fastapi import APIRouter

from src.crawler.fetcher import fetch_html
from src.crawler.extractor import extract_links
from src.services.scan_service import check_links


router = APIRouter(prefix="/scans", tags=["scans"])


class ScanRequest(BaseModel):
    urls: list[str]
    threads: int = 20
    timeout: int = 10



@router.post("")
def run_scan(request: ScanRequest):
    all_rows = []


    for url in request.urls:
        html = fetch_html(url, timeout=request.timeout)

        if not html:
            continue

        links = extract_links(url, html)

        if not links:
            continue

        rows = check_links(
            links=links,
            threads=request.threads,
            timeout=request.timeout,
            only_broken=False,
            crawl_id="api-scan"
        )

        all_rows.extend(rows)


        total_links = len(all_rows)
        broken_links = sum(1 for row in all_rows if row["Error"] or not row["OK"])
        ok_links = total_links - broken_links

        quality_score = round((ok_links / total_links) * 100, 2) if total_links else 0

        return{
            "total_links": total_links,
            "ok_links": ok_links,
            "broken_links": broken_links,
            "quality_score": quality_score,
            "results": all_rows
        }