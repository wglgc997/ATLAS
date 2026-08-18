# Quality Link Checker

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

Quality Link Checker is a local FastAPI web application for scanning a rendered web page, extracting links and page resources, validating them, and reviewing the results in a browser dashboard.

It is designed for pages where important links are created by JavaScript and are not available in the initial HTML.

## Features

- Local FastAPI dashboard
- JavaScript rendering with Playwright and Chromium
- Extraction of anchors, stylesheets, scripts, images, and iframes
- Relative URL resolution and fragment removal
- Optional filtering for external links and technical assets
- HTTP status validation with HEAD requests and GET fallback
- Redirect chain detection
- Response time measurement
- Detection of missing, empty, unsupported, and non-navigable href values
- Interaction checks for suspicious UI controls
- Local scan history saved in `data/scan_history.json`
- Backend-generated dashboard summary with health score and action counts
- Searchable, sortable, and filterable results table
- CSV export for the currently visible result set
- Optional SSL certificate verification and custom CA bundle support
- Configurable retries, timeouts, redirect limits, and Playwright wait strategy
- Automated tests for extraction, filtering, status classification, scan summaries, interaction handling, and history persistence

## Requirements

- Python 3.13
- Internet access for the first Playwright Chromium download
- Windows for the included `start.bat` launcher

The app can also run on Linux and macOS with the manual Python commands below.

## Quick Start on Windows

Clone the repository:

```powershell
git clone https://github.com/<your-user>/LinkChecker.git
cd LinkChecker
```

Run:

```powershell
.\start.bat
```

The script creates `.venv`, installs dependencies, installs Chromium into `playwright-browsers`, starts the app, and opens the dashboard.

The application runs at:

```text
http://127.0.0.1:8000
```

Keep the terminal window open while using the app. Press `Ctrl+C` to stop it.

## Manual Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install Chromium for Playwright:

```bash
python -m playwright install chromium
```

Start the application:

```bash
python launcher.py
```

Open:

```text
http://127.0.0.1:8000
```

## Usage

1. Open the dashboard.
2. Enter the page URL to scan.
3. Click `Analyze`.
4. Wait for Playwright to render the page and extract links.
5. Review the summary, priority issues, and full results table.
6. Use search, status filters, and sorting to focus the results.
7. Export the visible rows to CSV when needed.

Each scan is saved locally. Recent scans can be reloaded from the dashboard history panel.

## Configuration

The app works without a `.env` file by using defaults from `src/config/settings.py`.

Create a local `.env` file only when you need to override those defaults:

```env
HTTP_TIMEOUT=20
HTTP_RETRIES=2
HTTP_RETRY_BACKOFF=0.5
PLAYWRIGHT_TIMEOUT=60
PLAYWRIGHT_INTERACTION_TIMEOUT=3
VERIFY_SSL=true
CA_BUNDLE_PATH=
WAIT_UNTIL=domcontentloaded
MAX_REDIRECTS=10
```

| Variable | Default | Description |
| --- | --- | --- |
| `HTTP_TIMEOUT` | `20` | Per-link HTTP validation timeout in seconds. |
| `HTTP_RETRIES` | `2` | Number of retry attempts for timeout and connection failures. |
| `HTTP_RETRY_BACKOFF` | `0.5` | Backoff multiplier between retries. |
| `PLAYWRIGHT_TIMEOUT` | `60` | Page rendering timeout in seconds. |
| `PLAYWRIGHT_INTERACTION_TIMEOUT` | `3` | Timeout in seconds for interaction checks. |
| `VERIFY_SSL` | `true` | Enables SSL certificate verification. |
| `CA_BUNDLE_PATH` | empty | Optional path to a PEM certificate bundle. |
| `WAIT_UNTIL` | `domcontentloaded` | Playwright page load state used before extraction. |
| `MAX_REDIRECTS` | `10` | Maximum redirects allowed during HTTP validation. |

Set `VERIFY_SSL=false` only when scanning sites with invalid or internal certificates. For corporate environments, prefer keeping SSL verification enabled and setting `CA_BUNDLE_PATH`:

```env
VERIFY_SSL=true
CA_BUNDLE_PATH=C:\path\to\corporate-ca.pem
```

Do not commit `.env` files. They are ignored by Git.

## Status Classification

| Status | Meaning |
| --- | --- |
| `Valid` | HTTP 2xx response without redirects. |
| `Redirected` | The request followed at least one redirect and ended successfully. |
| `Redirect Loop` | Redirect handling exceeded the configured limit or ended on a 3xx response. |
| `Unauthorized` | HTTP 401 response. |
| `Forbidden` | HTTP 403 response. |
| `Broken` | Other HTTP 4xx response. |
| `Gone` | HTTP 410 response. |
| `Server Error` | HTTP 5xx response. |
| `Invalid Link` | Missing, empty, unsupported, or non-navigable href value. |
| `Interactive Element` | Suspicious element changed visible page state instead of navigating. |
| `Interaction Error` | Suspicious element did not navigate or produce a detectable interaction. |
| `SSL Error` | SSL certificate validation failed. |
| `Timeout` | The request timed out after retries. |
| `Connection Error` | The server could not be reached. |
| `DNS Error` | The domain name could not be resolved. |
| `Unknown Error` | Unexpected validation error. |

### Status Groups

Each result also includes `status_group`, a backend-generated category used by the dashboard for filtering and styling.

| Group | Meaning |
| --- | --- |
| `good` | Valid links and interactive elements that behaved correctly. |
| `redirected` | Links that redirected and ended successfully. |
| `broken` | Invalid links, HTTP failures, permission failures, redirect loops, or interaction errors. |
| `error` | Network, DNS, SSL, timeout, or unexpected validation errors. |
| `unknown` | Fallback group for unrecognized statuses. |

## API

Health check:

```text
GET /health
```

Dashboard:

```text
GET /
```

Run a scan:

```text
POST /scans
```

Example request:

```json
{
  "url": "https://example.com",
  "timeout": 20,
  "max_workers": 12,
  "include_assets": false,
  "include_external": true
}
```

Example response shape:

```json
{
  "source_page": "https://example.com",
  "total_links": 3,
  "good": 1,
  "redirected": 1,
  "broken": 1,
  "error": 0,
  "summary": {
    "total_links": 3,
    "good": 1,
    "redirected": 1,
    "broken": 1,
    "error": 0,
    "healthy_count": 2,
    "needs_action_count": 1,
    "health_score": 67,
    "health_state": "danger",
    "health_message": "1 link needs review.",
    "summary_message": "Scan completed. 1 of 3 links needs attention."
  },
  "results": [
    {
      "url": "https://example.com",
      "final_url": "https://example.com",
      "http_status": 200,
      "status": "Valid",
      "status_group": "good",
      "redirect_chain": [
        {
          "status_code": 200,
          "url": "https://example.com"
        }
      ],
      "response_time_ms": 120,
      "error_message": null,
      "source_page": "https://example.com",
      "link_text": "Example",
      "link_type": "anchor",
      "source_attribute": "href",
      "source_location": "Text link: Example"
    }
  ]
}
```

Scan history:

```text
GET /scans/history
GET /scans/history/{scan_id}
```

## Project Structure

```text
LinkChecker/
|-- data/
|   `-- scan_history.json
|-- src/
|   |-- api/
|   |-- checker/
|   |-- config/
|   |-- crawler/
|   |-- schemas/
|   |-- services/
|   |-- static/
|   |-- templates/
|   |-- utils/
|   `-- web.py
|-- tests/
|-- web/
|-- launcher.py
|-- start.bat
|-- LinkChecker.spec
|-- requirements.txt
|-- requirements-dev.txt
`-- README.md
```

## Development

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
```

Run the app directly with Uvicorn:

```bash
uvicorn src.web:app --reload --host 127.0.0.1 --port 8000
```

## Packaging

`LinkChecker.spec` is included for PyInstaller-based packaging. Build output and packaged binaries should not be committed.

## Roadmap

- [x] FastAPI backend
- [x] Browser rendering with Playwright
- [x] Link and resource extraction
- [x] HTTP validation
- [x] Windows launcher script
- [x] Core automated tests
- [x] Local scan history
- [x] CSV export
- [ ] Progress indicator during scans

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run the tests.
5. Open a pull request.

## License

This project is released under the MIT License. See `LICENSE` for details.
