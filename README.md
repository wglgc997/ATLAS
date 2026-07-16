
<p align="center">

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

</p>

<p align="center">

![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)
![Version](https://img.shields.io/badge/Version-2.0-informational?style=flat-square)

</p>

# 🔗 Link Checker

A Python-based web application that automatically crawls a webpage, extracts all available hyperlinks, validates each one, and presents the results through a simple web interface.

The project was created to eliminate manual link verification by providing a fast, browser-based solution capable of rendering JavaScript before extracting links.

---

## Features

- Web interface built with FastAPI
- JavaScript rendering using Playwright
- Automatic extraction of hyperlinks
- HTTP status validation
- Redirect detection
- Response time measurement
- Link classification
- Dashboard with scan results
- Modular architecture
- Ready for future SharePoint/Microsoft Graph integration

---

## Architecture

```
            +------------------+
            |  Web Browser     |
            +---------+--------+
                      |
                      |
                HTTP Request
                      |
                      ▼
             +----------------+
             |    FastAPI     |
             +-------+--------+
                     |
     +---------------+----------------+
     |                                |
     ▼                                ▼
Browser Extractor              Link Checker
 (Playwright)                   (requests)
     |                                |
     +---------------+----------------+
                     |
                     ▼
             Scan Service
                     |
                     ▼
            JSON Response
```

---

## Project Structure

```
LinkChecker/
│
├── src/
│   ├── api/
│   ├── checker/
│   ├── crawler/
│   ├── schemas/
│   ├── services/
│   ├── web/
│   └── utils/
│
├── static/
├── templates/
├── tests/
│
├── launcher.py
├── requirements.txt
├── Install.bat
├── LinkChecker.bat
└── README.md
```

---

## Technology Stack

- Python 3.13
- FastAPI
- Uvicorn
- Playwright
- Requests
- BeautifulSoup4
- Jinja2
- Pydantic
- Pytest

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-user>/LinkChecker.git

cd LinkChecker
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Playwright browsers:

```bash
playwright install chromium
```

Run the application:

```bash
python launcher.py
```

The application will be available at:

```
http://127.0.0.1:8000
```

---

## Usage

1. Enter the page URL.
2. Start a scan.
3. Wait for the page rendering.
4. Review the detected links.
5. Analyze HTTP status, redirects and response times.

---

## Current Status Classification

| Status | Description |
|---------|-------------|
| Good | HTTP 200 |
| Redirected | HTTP 3xx |
| Broken | HTTP 4xx, 5xx or request failure |

---

## Example Response

```json
{
  "source_page": "...",
  "total_links": 12,
  "good": 10,
  "redirected": 1,
  "broken": 1
}
```

---

## Roadmap

- [x] FastAPI backend
- [x] Browser rendering with Playwright
- [x] Automatic link extraction
- [x] HTTP validation
- [x] Dashboard
- [x] Batch execution (.bat)
- [ ] Progress indicator
- [ ] Historical scan results
- [ ] Docker support
- [ ] CI/CD pipeline
- [ ] GitHub Actions
- [ ] Kubernetes deployment

---

## Testing

Run all tests:

```bash
pytest
```

---

## Future Improvements

- Asynchronous link validation
- Retry mechanism
- Scheduled scans
- Authentication
- Export reports
- Performance metrics
- Accessibility analysis
- SEO checks
- Broken asset detection

---

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a Pull Request.

---

## License

This project is licensed under the MIT License.