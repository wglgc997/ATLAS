# Link Checker

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

Link Checker is a local web application that renders a webpage, extracts links and page resources, validates them, and shows the scan results in a browser dashboard.

It is useful for checking pages that need JavaScript rendering before links are available in the HTML.

## Features

- Local FastAPI web interface
- JavaScript rendering with Playwright and Chromium
- Extraction of anchors, stylesheets, scripts, images, and iframes
- Relative URL resolution
- HTTP status validation
- Redirect detection
- Response time measurement
- Link classification: `Good`, `Redirected`, `Broken`, `SSL Error`, `Timeout`, `Connection Error`, `DNS Error`, and `Unknown Error`
- Friendly error descriptions with separate technical details
- Optional SSL certificate verification and custom CA bundle support
- Configurable HTTP retries, timeouts, redirects, and Playwright wait strategy
- Automated tests for core extraction, status classification, and scan summaries

## Requirements

- Python 3.13
- Internet access for the first Playwright Chromium download
- Windows for the included `.bat` launcher scripts

The app can also run on Linux and macOS through the manual Python commands below.

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

The script will:

- Find Python
- Create `.venv`
- Install dependencies from `requirements.txt`
- Install Chromium for Playwright into `playwright-browsers`
- Start the local app
- Open the dashboard in your default browser

The application runs at:

```text
http://127.0.0.1:8000
```

Keep the terminal window open while using the app. Press `Ctrl+C` to stop it.

## Manual Installation

Clone the repository:

```bash
git clone https://github.com/<your-user>/LinkChecker.git
cd LinkChecker
```

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

## Configuration

The app works without a `.env` file by using the defaults defined in `src/config/settings.py`.

You can create a local `.env` file only when you need to override those defaults:

```env
HTTP_TIMEOUT=20
HTTP_RETRIES=2
HTTP_RETRY_BACKOFF=0.5
PLAYWRIGHT_TIMEOUT=60
VERIFY_SSL=true
CA_BUNDLE_PATH=
WAIT_UNTIL=domcontentloaded
MAX_REDIRECTS=10
```

`HTTP_TIMEOUT` controls each HTTP request used to validate links.

`PLAYWRIGHT_TIMEOUT` controls page rendering and link discovery with Playwright.

Set `VERIFY_SSL=false` only when you need to scan sites with invalid or internal SSL certificates.

For corporate environments, prefer keeping `VERIFY_SSL=true` and setting `CA_BUNDLE_PATH` to a PEM certificate bundle:

```env
VERIFY_SSL=true
CA_BUNDLE_PATH=C:\path\to\corporate-ca.pem
```

Do not commit `.env` files. They are ignored by Git.

## Usage

1. Open the dashboard.
2. Enter the page URL to scan.
3. Start the scan.
4. Wait for Playwright to render the page and extract links.
5. Review each result, including status, final URL, response time, link type, and source location.

## Status Classification

| Status | Description |
| --- | --- |
| `Good` | Successful response, usually HTTP 2xx |
| `Redirected` | Redirect detected or HTTP 3xx |
| `Broken` | HTTP 4xx or HTTP 5xx |
| `SSL Error` | SSL certificate validation failed |
| `Timeout` | The request timed out after retries |
| `Connection Error` | The server could not be reached |
| `DNS Error` | The domain name could not be resolved |
| `Unknown Error` | Unexpected validation error |

## Project Structure

```text
LinkChecker/
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
|-- LinkChecker.bat
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

## API

Health check:

```text
GET /health
```

Main dashboard:

```text
GET /
```

Scan endpoints are defined in `src/api/scans.py`.

## Roadmap

- [x] FastAPI backend
- [x] Browser rendering with Playwright
- [x] Link and resource extraction
- [x] HTTP validation
- [x] Windows launcher script
- [x] Core automated tests
- [x] Exportable reports
- [ ] Progress indicator during scans


## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run the tests.
5. Open a pull request.

## License

This project is released under the MIT License. See `LICENSE` for details.
