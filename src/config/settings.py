from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


def str_to_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "yes")

VERIFY_SSL = str_to_bool(os.getenv("VERIFY_SSL", "true"))