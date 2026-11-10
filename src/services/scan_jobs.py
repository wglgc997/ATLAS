import threading
from collections.abc import Callable
from time import monotonic
from uuid import uuid4

from src.schemas.scan import ScanJobResponse, ScanJobStatus, ScanRequest

JOB_TTL_SECONDS = 15 * 60


class ScanJobStore:
    """In-memory job store for the single-process local application."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict] = {}
        self._condition = threading.Condition()

    def create(
        self,
        request: ScanRequest,
        runner: Callable[[ScanRequest, Callable[[dict], None]], object],
    ) -> ScanJobResponse:
        self._remove_expired()
        job_id = str(uuid4())
        urls = [str(request.url)] + ([str(request.url_2)] if request.url_2 else [])
        job = {
            "id": job_id,
            "status": ScanJobStatus.PENDING,
            "stage": "queued",
            "active_url": None,
            "total_urls": len(urls),
            "completed_urls": 0,
            "total_links": 0,
            "checked_links": 0,
            "error": None,
            "result": None,
            "progress": {},
            "revision": 0,
            "updated_at": monotonic(),
        }
        with self._condition:
            self._jobs[job_id] = job

        thread = threading.Thread(
            target=self._run,
            args=(job_id, request, runner),
            daemon=True,
            name=f"scan-job-{job_id}",
        )
        thread.start()
        return self._response(job)

    def _run(self, job_id: str, request: ScanRequest, runner: Callable) -> None:
        self._update(job_id, status=ScanJobStatus.RUNNING, stage="starting")
        try:
            result = runner(request, lambda update: self._progress(job_id, update))
            self._update(job_id, status=ScanJobStatus.COMPLETED, stage="completed", result=result)
        except Exception as error:
            self._update(job_id, status=ScanJobStatus.FAILED, stage="failed", error=str(error) or "Scan failed.")

    def _progress(self, job_id: str, update: dict) -> None:
        url = update.get("url")
        with self._condition:
            job = self._jobs.get(job_id)
            if not job:
                return
            if url:
                job["progress"][url] = update
            progress = list(job["progress"].values())
            job["active_url"] = url
            job["stage"] = update.get("stage", job["stage"])
            job["total_links"] = sum(item.get("total_links", 0) for item in progress)
            job["checked_links"] = sum(item.get("checked_links", 0) for item in progress)
            job["completed_urls"] = sum(
                item.get("stage") == "building" for item in progress
            )
            self._touch(job)

    def _update(self, job_id: str, **changes: object) -> None:
        with self._condition:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.update(changes)
            self._touch(job)

    def _touch(self, job: dict) -> None:
        job["revision"] += 1
        job["updated_at"] = monotonic()
        self._condition.notify_all()

    def get(self, job_id: str) -> ScanJobResponse | None:
        with self._condition:
            job = self._jobs.get(job_id)
            return self._response(job) if job else None

    def wait_for_update(self, job_id: str, revision: int) -> tuple[ScanJobResponse | None, int]:
        with self._condition:
            job = self._jobs.get(job_id)
            if not job:
                return None, revision
            if job["revision"] == revision:
                self._condition.wait(timeout=15)
            job = self._jobs.get(job_id)
            if not job:
                return None, revision
            return self._response(job), job["revision"]

    def _response(self, job: dict) -> ScanJobResponse:
        return ScanJobResponse(**{key: value for key, value in job.items() if key not in {"progress", "revision", "updated_at"}})

    def _remove_expired(self) -> None:
        threshold = monotonic() - JOB_TTL_SECONDS
        with self._condition:
            self._jobs = {
                job_id: job for job_id, job in self._jobs.items()
                if job["updated_at"] >= threshold
            }


scan_jobs = ScanJobStore()
