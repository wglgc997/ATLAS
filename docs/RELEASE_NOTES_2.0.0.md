# ATLAS 2.0.0

Release date: November 10, 2026

ATLAS 2.0 introduces faster, more resilient multi-page scanning and a clearer local workflow for teams.

## Highlights

### Scan up to two URLs at once

- URL 1 remains required; URL 2 is optional.
- Both URLs use the same timeout, worker, external-link, and asset settings.
- Each page is scanned independently, and a failure in one scan does not discard the other result.
- Results are displayed in separate tabs.
- Single-URL scans continue to use the existing response format and workflow.

### Improved local history

- Scans submitted together share a common `batch_id` in local history.
- Each successful page scan is saved independently.
- Added a **Clear history** action in the dashboard, with a confirmation prompt.
- Added `DELETE /scans/history` for clearing the local history programmatically.

### Live scan progress

- The dashboard now shows real scan progress instead of simulated loading steps.
- Progress includes rendering, extraction, validation, report generation, and the current link count.
- Added local in-memory scan jobs with automatic expiration after 15 minutes.
- Added the following API endpoints:
  - `POST /scans/jobs`
  - `GET /scans/jobs/{job_id}`
  - `GET /scans/jobs/{job_id}/events` (Server-Sent Events)
- The original `POST /scans` endpoint remains available for existing integrations.

### Faster scans

- Two-page scans now run concurrently.
- HTTP connections are reused per worker where possible.
- Browser interaction checks are limited to reduce long sequential waits on JavaScript-heavy pages.
- Default interaction timeout was reduced to one second.
- Added `MAX_INTERACTION_CHECKS` and `BROWSER_CHANNEL` configuration options.

### More accurate link results

- Fragment-only anchors such as `#` and `#section` are recognized as in-page navigation.
- These anchors are no longer reported as invalid links or counted as broken results.

### Corporate Windows environments

- ATLAS first tries the bundled Playwright Chromium browser.
- If that browser is blocked by an Application Control policy, ATLAS automatically falls back to the installed Microsoft Edge browser.
- Set `BROWSER_CHANNEL=msedge` in `.env` to force Microsoft Edge.

## Configuration

New or updated optional `.env` settings:

```env
PLAYWRIGHT_INTERACTION_TIMEOUT=1
MAX_INTERACTION_CHECKS=5
BROWSER_CHANNEL=auto
```

`BROWSER_CHANNEL=auto` uses bundled Chromium first and then Microsoft Edge if Chromium cannot start.

## Distribution

Windows users can extract `LinkChecker-user.zip` and run `start.bat`. The launcher creates its virtual environment, installs dependencies, downloads the required Playwright browser files, and starts ATLAS.

## Upgrade notes

- Replace the previous `LinkChecker-user` folder with the 2.0.0 package.
- Run `start.bat` from the new folder.
- Existing local scan history remains compatible.
