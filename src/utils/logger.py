import logging

from pathlib import Path

"""
create the folder
create the handlers
configure logging
"""

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "link_checker.log"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure application logging."""

    LOG_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )