from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


def str_to_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "yes")

def str_to_int(value: str, default: int) -> int:
    try:
        return int(value)
    except ValueError:
        return default

def str_to_float(value: str, default: float) -> float:
    try:
        return float(value)
    except ValueError:
        return default


HTTP_TIMEOUT = str_to_int(os.getenv("HTTP_TIMEOUT", "20"), 20)
HTTP_RETRIES = str_to_int(os.getenv("HTTP_RETRIES", "2"), 2)
HTTP_RETRY_BACKOFF = str_to_float(os.getenv("HTTP_RETRY_BACKOFF", "0.5"), 0.5)

PLAYWRIGHT_TIMEOUT = str_to_int(os.getenv("PLAYWRIGHT_TIMEOUT", "60"), 60)
PLAYWRIGHT_INTERACTION_TIMEOUT = str_to_int(
    os.getenv("PLAYWRIGHT_INTERACTION_TIMEOUT", "3"),
    3,
)

VERIFY_SSL = str_to_bool(os.getenv("VERIFY_SSL", "true"))
CA_BUNDLE_PATH = os.getenv("CA_BUNDLE_PATH")

WAIT_UNTIL = os.getenv("WAIT_UNTIL", "domcontentloaded")
MAX_REDIRECTS = str_to_int(os.getenv("MAX_REDIRECTS", "10"),10)


