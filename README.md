# ATLAS

> A link checker and website quality analysis tool focused on reliability, accessibility, relevance, authority, and performance.

![demo](docs/images/gif-ezgif.com-video-to-gif-converter.gif)

![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat-square&logo=playwright&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

ATLAS helps developers, QA teams, and content owners find broken links, redirects, certificate problems, timeouts, and unreachable resources without checking every URL manually.

Unlike a basic HTML crawler, it uses Playwright to render JavaScript-powered pages before extracting and validating their content. One or two pages can be analyzed per request, with independent results presented in a searchable local dashboard.

## ✨ Highlights

- **JavaScript-aware scanning** with Playwright and Chromium
- **Actionable classification** for valid, redirected, broken, and unreachable links
- **Page health score** with a summary of items that need attention
- **Detailed diagnostics** including response time, final URL, redirect chain, and error details
- **Flexible scope** with optional external-link and technical-asset scanning
- **Two-page scans** with separate result tabs and independent failure handling
- **Local-first workflow** with grouped scan history, history cleanup, and CSV export
- **Performance safeguards** for browser interactions and reusable HTTP connections
- **Simple Windows launcher** that prepares the environment and opens the application

## 🚀 Quick Start

### Requirements

- Windows 10 or later, or a supported Linux distribution
- Python 3.13 or later available on `PATH`
- Internet access during the first setup to download Chromium

### Windows

Clone the repository and open its directory:

```powershell
git clone [https://github.com/wglgc997/ATLAS.git]
cd ATLAS
```

Start the application:

```powershell
.\start.bat
```

The launcher automatically:

1. Creates a local virtual environment.
2. Installs the Python dependencies.
3. Downloads or verifies Playwright Chromium.
4. Starts the FastAPI application.
5. Opens the dashboard in your default browser.

The application is available at `http://127.0.0.1:8000`. Keep the terminal open while using it and press `Ctrl+C` to stop the server.

For the ready-to-use Windows package, extract `release/LinkChecker-user.zip` and run its `start.bat`. The script creates its own virtual environment and downloads Chromium on first use.

### Linux

Clone the repository and open its directory:

```bash
git clone [https://github.com/wglgc997/ATLAS.git]
cd ATLAS
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the application dependencies and Playwright Chromium:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install --with-deps chromium
```

Start the application:

```bash
python launcher.py
```

Open `http://127.0.0.1:8000` if the dashboard does not open automatically. Keep the terminal running and press `Ctrl+C` to stop the application.

## 🖥️ Using the Dashboard

1. Enter URL 1 (required) and, optionally, URL 2.
2. Choose whether to include external links and technical assets; the same settings apply to both URLs.
3. Start the analysis. The pages run independently, so a failure in one does not prevent the other result.
4. Use the result tabs to switch between URL 1 and URL 2.
5. Review the health score and prioritized summary, then filter, search, sort, or export the visible result set to CSV.
6. Reopen a saved scan from the local history, or use **Clear history** to permanently remove all local entries after confirmation.

Every successful scan is stored locally in `data/scan_history.json`. Scans submitted together share a `batch_id`, which makes them identifiable as one user-initiated batch.

## 🔍 What the Scanner Detects

| Category | Examples |
| --- | --- |
| Healthy | Successful HTTP 2xx responses and working interactive elements |
| Redirected | Links that follow one or more redirects and reach a valid destination |
| Broken | HTTP 4xx/5xx responses, invalid links, permission failures, and redirect loops |
| Connection errors | DNS failures, timeouts, SSL errors, and unreachable servers |
| Page resources | Anchors, images, scripts, stylesheets, and iframes |

Fragment-only anchors such as `#section` are local page navigation and are excluded from HTTP validation, so they do not appear as invalid links. Each result may include its original URL, final URL, HTTP status, redirect chain, response time, source element, and a human-readable explanation.

## 🏗️ How It Works

```mermaid
flowchart TD
    A["One or two URLs submitted"] --> B["Pages analyzed independently"]
    B --> C["Each page rendered with Playwright"]
    C --> D["Links and resources extracted"]
    D --> E["URLs validated in parallel"]
    E --> F["Separate tabs, grouped history, and CSV"]
```

The application follows a layered design: the FastAPI routes receive scan requests, the crawler renders and extracts page content, services normalize and filter URLs, and the checker validates each resource before the summary is generated.

## 🛠️ Manual Installation

The Windows launcher is the simplest setup option. The application can also be configured manually on Windows, Linux, or macOS:

```bash
python -m venv .venv
```

Activate the environment:

```powershell
# Windows
.\.venv\Scripts\activate
```

```bash
# Linux or macOS
source .venv/bin/activate
```

Install the application and Chromium:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
python launcher.py
```

## ⚙️ Configuration

The application works without a `.env` file. Create one in the project root only when you need to override the defaults:

```env
HTTP_TIMEOUT=20
HTTP_RETRIES=2
HTTP_RETRY_BACKOFF=0.5
PLAYWRIGHT_TIMEOUT=60
PLAYWRIGHT_INTERACTION_TIMEOUT=1
MAX_INTERACTION_CHECKS=5
BROWSER_CHANNEL=auto
VERIFY_SSL=true
CA_BUNDLE_PATH=
WAIT_UNTIL=domcontentloaded
MAX_REDIRECTS=10
```

| Variable | Default | Purpose |
| --- | --- | --- |
| `HTTP_TIMEOUT` | `20` | Maximum time for each HTTP validation request |
| `HTTP_RETRIES` | `2` | Retry attempts for connection failures and timeouts |
| `HTTP_RETRY_BACKOFF` | `0.5` | Delay multiplier between retries |
| `PLAYWRIGHT_TIMEOUT` | `60` | Maximum page rendering time |
| `PLAYWRIGHT_INTERACTION_TIMEOUT` | `1` | Maximum time for an interaction check; lower values improve scan speed |
| `MAX_INTERACTION_CHECKS` | `5` | Maximum number of JavaScript-like controls checked per page; caps sequential browser work |
| `BROWSER_CHANNEL` | `auto` | Uses bundled Chromium first, then Microsoft Edge if Chromium is blocked; set to `msedge` to force Edge |
| `VERIFY_SSL` | `true` | Enables SSL certificate verification |
| `CA_BUNDLE_PATH` | Empty | Optional path to a trusted PEM certificate bundle |
| `WAIT_UNTIL` | `domcontentloaded` | Playwright page-load state used before extraction |
| `MAX_REDIRECTS` | `10` | Maximum redirects followed during validation |

For internal websites with a private certificate authority, keep verification enabled and configure the certificate bundle:

```env
VERIFY_SSL=true
CA_BUNDLE_PATH=C:\path\to\corporate-ca.pem
```

Use `VERIFY_SSL=false` only in a controlled environment. Never commit `.env` files or private certificates.

## 🔌 API

FastAPI provides interactive API documentation at `http://127.0.0.1:8000/docs` while the application is running.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check application availability |
| `GET` | `/` | Open the dashboard |
| `POST` | `/scans` | Analyze a page |
| `POST` | `/scans/jobs` | Start a scan job and return its ID immediately |
| `GET` | `/scans/jobs/{job_id}` | Retrieve the latest job status |
| `GET` | `/scans/jobs/{job_id}/events` | Stream live job updates via Server-Sent Events |
| `GET` | `/scans/history` | List locally stored scans |
| `DELETE` | `/scans/history` | Permanently clear the local scan history |
| `GET` | `/scans/history/{scan_id}` | Retrieve a stored scan |

Example scan request:

```json
{
  "url": "https://example.com",
  "url_2": "https://example.org",
  "timeout": 20,
  "max_workers": 12,
  "include_assets": false,
  "include_external": true
}
```

`url` is required and `url_2` is optional. A request with only `url` retains the original single-scan response format. With two URLs, the response contains a `batch_id` and one independent outcome for each page.

## 📁 Project Structure

```text
Quality-Link-Checker/
├── data/                   # Local scan history
├── src/
│   ├── api/                # FastAPI routes
│   ├── checker/            # HTTP validation
│   ├── config/             # Runtime settings
│   ├── crawler/            # HTML and browser extraction
│   ├── schemas/            # API data models
│   ├── services/           # Scan orchestration and summaries
│   ├── static/             # Dashboard CSS and JavaScript
│   ├── templates/          # Dashboard templates
│   └── web.py              # FastAPI application
├── tests/                  # Automated tests
├── launcher.py             # Local application launcher
├── start.bat               # Windows setup and startup script
├── requirements.txt        # Runtime dependencies
└── requirements-dev.txt    # Development tools
```

## 🧪 Development

Install the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run the tests:

```bash
python -m pytest
```

Start the application with automatic reload:

```bash
uvicorn src.web:app --reload --host 127.0.0.1 --port 8000
```

## ⚠️ Current Limitations

- The application scans up to two pages per request; it does not crawl an entire website recursively.
- Some websites may block automated HTTP requests or browser automation.
- Scan history is stored locally and is not synchronized between computers.
- Windows provides the automated `start.bat` setup; Linux and macOS currently use the documented manual setup.

## 🗺️ Roadmap

- [x] JavaScript-rendered page scanning
- [x] Link and resource validation
- [x] Page health score and prioritized summary
- [x] Searchable and filterable dashboard
- [x] Local scan history
- [x] Two-page scans with separate result tabs
- [x] Local history cleanup
- [x] CSV export
- [x] Core automated tests
- [x] Live progress feedback during long scans
- [x] Packaged Windows release

## 🤝 Contributing

Bug reports, ideas, and pull requests are welcome. To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Open a pull request describing the problem and your solution.

You can also [open an issue](https://github.com/wglgc997/Quality-Link-Checker/issues) to report a bug or suggest an improvement.

## 👤 Author

Created by [Wagner Carvalho](https://github.com/wglgc997) as a practical project in Python backend development, browser automation, web quality analysis, and local application distribution.

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
