import json

from datetime import datetime, timezone
from uuid import uuid4

from src.schemas.scan import ScanResponse
from src.utils.runtime_paths import get_bundle_directory

HISTORY_LIMIT = 50
HISTORY_FILE = get_bundle_directory() / "data" / "scan_history.json"

def load_scan_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []

    with HISTORY_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

        return data if isinstance(data, list) else []

def list_scan_history() -> list[dict]:
    return [
        {
            "id": item.get("id"),
            "created_at": item.get("created_at"),
            "source_page": item.get("source_page"),
            "total_links": item.get("total_links", 0),
            "good": item.get("good", 0),
            "redirected": item.get("redirected", 0),
            "broken": item.get("broken", 0),
            "error": item.get("error", 0),
        }

        for item in load_scan_history()
        if item.get("id")
    ]

def get_scan_from_history(scan_id: str) -> dict | None:
    for item in load_scan_history():
        if item.get("id") == scan_id:
            return item

    return None

def save_scan_to_history(scan: ScanResponse) -> dict:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    item = {
        "id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        **scan.model_dump(mode="json")
    }

    history = [item, *load_scan_history()[:HISTORY_LIMIT]]
    temporary_file = HISTORY_FILE.with_name(f"{HISTORY_FILE.stem}.{item['id']}.tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=2, ensure_ascii=False)

    temporary_file.replace(HISTORY_FILE)

    return item
