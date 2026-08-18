import os
from pathlib import Path

BROWSER_DIRECTORY_NAME = "playwright-browsers"
CHROMIUM_EXECUTABLE_NAME = "chrome-headless-shell.exe"


def get_bundle_directory() -> Path:
    """
    Return the directory containing bundled application resources.

    In development, the resources are located in the project root.
    In a PyInstaller build, the resources are located relative to the
    bundle
    """

    return Path(__file__).resolve().parents[2]


def get_playwright_browser_directory() -> Path:
    """
    Return the absolute path to the Playwright browser directory.

    Returns:
        Directory containing the bundled Chromium installation.
    """
    configured_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")

    if configured_path:
        return Path(configured_path)

    return get_bundle_directory() / BROWSER_DIRECTORY_NAME


def configure_playwright_browser_path() -> Path:
    """
     Configure Playwright to use the bundled browser installation.

     Returns:
         The configured Playwright browsers directory.

    Raises:
        FileNotFoundError: If the bundled browser directory is missing.
     """
    browser_directory = get_playwright_browser_directory()

    if not browser_directory.exists():
        raise FileNotFoundError(
            "The Playwright browser directory was not found: "
            f"{browser_directory}"
        )
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_directory)

    return browser_directory


def find_chromium_executable() -> Path:
    """
    Find the bundled Chromium headless executable.

    The exact Chromium directory includes a Playwright revision number,
    so the executable is located dynamically instead of using a fixed
    version-specific path.

    Returns:
           Absolute path to the Chromium headless executable.

    Raises:
           FileNotFoundError: If Chromium cannot be found.
     """

    browser_directory = get_playwright_browser_directory()

    if not browser_directory.exists():
        raise FileNotFoundError(
            "The Playwright browsers directory was not found: "
            f"{browser_directory}"
        )

    executable_candidates = list(
        browser_directory.rglob(CHROMIUM_EXECUTABLE_NAME)
    )

    if not executable_candidates:
        raise FileNotFoundError(
            "The bundled Chromium executable was not found inside: "
            f"{browser_directory}"
        )
    return executable_candidates[0]
