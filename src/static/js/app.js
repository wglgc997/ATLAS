const scanForm = document.getElementById("scan-form");
const pageUrlInput = document.getElementById("page-url");
const scanButton = document.getElementById("scan-button");
const formError = document.getElementById("form-error");
const appStatus = document.getElementById("app-status");
const appStatusText = document.getElementById("app-status-text");
const historyList = document.getElementById("history-list");
const historyPanel = document.getElementById("history-panel");
const historySubtitle = document.getElementById("history-subtitle");
const refreshHistoryButton = document.getElementById("refresh-history-button");
const toggleHistoryButton = document.getElementById("toggle-history-button");

const emptySection = document.getElementById("empty-section");
const loadingSection = document.getElementById("loading-section");
const loadingUrlElement = document.getElementById("loading-url");
const resultsSection = document.getElementById("results-section");

const totalLinksElement = document.getElementById("total-links");
const goodLinksElement = document.getElementById("good-links");
const redirectedLinksElement = document.getElementById("redirected-links");
const brokenLinksElement = document.getElementById("broken-links");
const errorLinksElement = document.getElementById("error-links");
const healthScoreElement = document.getElementById("health-score");
const healthMessageElement = document.getElementById("health-message");
const scanSummaryMessageElement = document.getElementById("scan-summary-message");
const distributionBar = document.getElementById("distribution-bar");
const needsActionFilterButton = document.getElementById("needs-action-filter");
const issuesSubtitleElement = document.getElementById("issues-subtitle");
const issuesList = document.getElementById("issues-list");
const toggleIssuesButton = document.getElementById("toggle-issues-button");

const sourcePageElement = document.getElementById("source-page");
const resultsTableBody = document.getElementById("results-table-body");
const resultsSearchInput = document.getElementById("results-search");
const statusFilter = document.getElementById("status-filter");
const exportCsvButton = document.getElementById("export-csv-button");

let currentResults = [];
let currentSourcePage = "";
let selectedHistoryScanId = "";
let currentSort = {
    key: null,
    direction: "asc",
};
let quickFilter = "all";


function formatHistoryDate(value) {
    if (!value) {
        return "Unknown date";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "Unknown date";
    }

    return date.toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    });
}


/**
 * Update the compact status indicator in the app header.
 */
function setAppStatus(status, label) {
    appStatus.dataset.status = status;
    appStatusText.textContent = label;
}


/**
 * Fallback for older scan history entries without status_group.
 */
function normalizeStatus(status) {
    if (!status) {
        return "unknown";
    }

    const normalizedStatus = status
        .toString()
        .trim()
        .toLowerCase();

    if (
        normalizedStatus === "good" ||
        normalizedStatus === "ok" ||
        normalizedStatus === "valid" ||
        normalizedStatus === "interactive element"
    ) {
        return "good";
    }

    if (
        normalizedStatus === "redirected" ||
        normalizedStatus === "redirect"
    ) {
        return "redirected";
    }

    if (
        normalizedStatus === "broken" ||
        normalizedStatus === "failed" ||
        normalizedStatus === "unauthorized" ||
        normalizedStatus === "forbidden" ||
        normalizedStatus === "gone" ||
        normalizedStatus === "server error" ||
        normalizedStatus === "invalid link" ||
        normalizedStatus === "redirect loop" ||
        normalizedStatus === "interaction error"
    ) {
        return "broken";
    }

    if (
        normalizedStatus == "ssl error" ||
        normalizedStatus == "timeout" ||
        normalizedStatus == "connection error" ||
        normalizedStatus == "dns error" ||
        normalizedStatus == "unknown error" ||
        normalizedStatus == "error"
    ) {
        return "error";
    }

    return "unknown"
}


function getStatusGroup(result) {
    return result.status_group || normalizeStatus(result.status);
}


/**
 * Convert the internal status value into readable text.
 */
function getStatusLabel(status, rawStatus = null) {
    const labels = {
        good: "Valid",
        redirected: "Redirected",
        broken: rawStatus || "Broken",
        error: rawStatus || "Error",
        unknown: "Unknown",
    };

    return labels[status] || labels.unknown;
}


/**
 * Return true when a row requires user review or correction.
 */
function needsAction(result) {
    const statusGroup = getStatusGroup(result);

    return statusGroup === "broken" || statusGroup === "error";
}


/**
 * Prevent raw API values from being inserted as HTML.
 */
function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return value
        .toString()
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/**
 * Return true for values that are safe enough to expose as links.
 */
function isClickableUrl(value) {
    if (!value) {
        return false;
    }

    const trimmedValue = value.toString().trim();

    if (!trimmedValue) {
        return false;
    }

    return !/^(javascript|data|vbscript):/i.test(trimmedValue);
}


/**
 * Render plain text with a copy action.
 */
function renderCopyableValue(value, label) {
    if (!value) {
        return "-";
    }

    const escapedValue = escapeHtml(value);

    return `
        <div class="url-content">
            <span>${escapedValue}</span>

            <button
                class="copy-button"
                type="button"
                data-copy="${escapedValue}"
                aria-label="Copy ${escapeHtml(label)}"
            >
                Copy
            </button>
        </div>
    `;
}


/**
 * Render a URL with open and copy actions.
 */
function renderUrlCell(value, label) {
    if (!value) {
        return "-";
    }

    if (!isClickableUrl(value)) {
        return renderCopyableValue(value, label);
    }

    const escapedValue = escapeHtml(value);

    return `
        <div class="url-content">
            <a
                class="url-link"
                href="${escapedValue}"
                target="_blank"
                rel="noopener noreferrer"
            >
                ${escapedValue}
            </a>

            <button
                class="copy-button"
                type="button"
                data-copy="${escapedValue}"
                aria-label="Copy ${escapeHtml(label)}"
            >
                Copy
            </button>
        </div>
    `;
}


/**
 * Return the fields included in text search.
 */
function getSearchableText(result) {
    return [
        result.status,
        result.http_status,
        result.url,
        result.final_url,
        formatRedirectChain(result.redirect_chain),
        result.response_time_ms,
        result.source_location,
        result.link_type,
        result.source_attribute,
        result.error_message,
    ]
        .filter((value) => value !== null && value !== undefined)
        .join(" ")
        .toLowerCase();
}


/**
 * Return a normalized sort value for a result row.
 */
function getSortValue(result, key) {
    if (key === "status") {
        return getStatusLabel(getStatusGroup(result), result.status)
    }

    return result[key] ?? "";
}


/**
 * Filter, search, and sort result rows for table display and export.
 */
function getVisibleResults(results) {
    const selectedStatus = statusFilter.value;
    const searchTerm = resultsSearchInput.value.trim().toLowerCase();

    const filteredResults = results.filter((result) => {
        const statusGroup = getStatusGroup(result);
        const matchesQuickFilter = (
            quickFilter !== "needs-action" ||
            needsAction(result)
        );

        const matchesStatus = (
            selectedStatus === "all" ||
            statusGroup === selectedStatus
        );

        const matchesSearch = (
            searchTerm === "" ||
            getSearchableText(result).includes(searchTerm)
        );

        return matchesQuickFilter && matchesStatus && matchesSearch;
    });

    if (!currentSort.key) {
        return filteredResults;
    }

    return [...filteredResults].sort((left, right) => {
        const leftValue = getSortValue(left, currentSort.key);
        const rightValue = getSortValue(right, currentSort.key);

        if (
            currentSort.key === "http_status" ||
            currentSort.key === "response_time_ms"
        ) {
            const leftNumber = Number(leftValue);
            const rightNumber = Number(rightValue);

            if (Number.isNaN(leftNumber) && Number.isNaN(rightNumber)) {
                return 0;
            }

            if (Number.isNaN(leftNumber)) {
                return 1;
            }

            if (Number.isNaN(rightNumber)) {
                return -1;
            }

            return currentSort.direction === "asc"
                ? leftNumber - rightNumber
                : rightNumber - leftNumber;
        }

        const comparison = leftValue
            .toString()
            .localeCompare(rightValue.toString(), undefined, {
                numeric: true,
                sensitivity: "base",
            });

        return currentSort.direction === "asc"
            ? comparison
            : -comparison;
    });
}


/**
 * Update visual sort direction labels on sortable headers.
 */
function updateSortButtons() {
    document.querySelectorAll(".sort-button").forEach((button) => {
        const isActive = button.dataset.sortKey === currentSort.key;

        button.dataset.active = isActive ? "true" : "false";
        button.dataset.direction = isActive
            ? currentSort.direction
            : "";
    });
}


/**
 * Escape a value for RFC 4180-style CSV output.
 */
function escapeCsvValue(value) {
    if (value === null || value === undefined) {
        return "";
    }

    const stringValue = value.toString();

    if (/[",\r\n]/.test(stringValue)) {
        return `"${stringValue.replaceAll('"', '""')}"`;
    }

    return stringValue;
}


/**
 * Render the redirect status chain as compact text.
 */
function formatRedirectChain(redirectChain) {
    if (!Array.isArray(redirectChain) || redirectChain.length === 0) {
        return "";
    }

    return redirectChain
        .map((step) => step.status_code ?? "-")
        .join(" -> ");
}


/**
 * Build a portable filename for exported scan results.
 */
function buildCsvFilename() {
    const timestamp = new Date()
        .toISOString()
        .replaceAll(":", "-")
        .replace(/\.\d{3}Z$/, "Z");

    const statusSuffix = statusFilter.value === "all"
        ? "all"
        : statusFilter.value;

    return `link-checker-${statusSuffix}-${timestamp}.csv`;
}


/**
 * Download the currently filtered scan results as CSV.
 */
function exportCurrentResultsToCsv() {
    const filteredResults = getVisibleResults(currentResults);

    if (filteredResults.length === 0) {
        formError.textContent = "There are no rows to export for this filter.";
        formError.classList.remove("hidden");

        return;
    }

    const headers = [
        "source_page",
        "status",
        "http_status",
        "url",
        "final_url",
        "redirect_chain",
        "response_time_ms",
        "source_location",
        "link_type",
        "source_attribute",
        "error_message",
    ];

    const rows = filteredResults.map((result) => [
        currentSourcePage,
        getStatusLabel(getStatusGroup(result), result.status),
        result.http_status ?? "",
        result.url ?? "",
        result.final_url ?? "",
        formatRedirectChain(result.redirect_chain),
        result.response_time_ms ?? "",
        result.source_location ?? "",
        result.link_type ?? "",
        result.source_attribute ?? "",
        result.error_message ?? "",
    ]);

    const csvContent = [
        headers,
        ...rows,
    ]
        .map((row) => row.map(escapeCsvValue).join(","))
        .join("\r\n");

    const blob = new Blob([csvContent], {
        type: "text/csv;charset=utf-8",
    });

    const downloadUrl = URL.createObjectURL(blob);
    const downloadLink = document.createElement("a");

    downloadLink.href = downloadUrl;
    downloadLink.download = buildCsvFilename();
    downloadLink.click();

    URL.revokeObjectURL(downloadUrl);
}


/**
 * Render the scan summary cards.
 */
function renderSummary(data) {
    currentSourcePage = data.source_page ?? "";

    const summary = data.summary || {};
    const total = summary.total_links ?? data.total_links ?? 0;
    const good = summary.good ?? data.good ?? 0;
    const redirected = summary.redirected ?? data.redirected ?? 0;
    const broken = summary.broken ?? data.broken ?? 0;
    const error = summary.error ?? data.error ?? 0;
    const healthScore = summary.health_score ?? 0;
    const healthState = summary.health_state || "unknown";
    const healthMessage = summary.health_message ||
        "Summary unavailable for this saved scan.";
    const summaryMessage = summary.summary_message ||
        "Summary unavailable for this saved scan.";

    totalLinksElement.textContent = total;
    goodLinksElement.textContent = good;
    redirectedLinksElement.textContent = redirected;
    brokenLinksElement.textContent = broken;
    errorLinksElement.textContent = error;
    healthScoreElement.textContent = `${healthScore}%`;
    healthScoreElement.dataset.health = healthState;
    healthMessageElement.textContent = healthMessage;
    scanSummaryMessageElement.textContent = summaryMessage;

    sourcePageElement.textContent = data.source_page
        ? `Source page: ${data.source_page}`
        : "";

    renderDistributionBar({
        total,
        good,
        redirected,
        broken,
        error,
    });
}


/**
 * Render a proportional status bar so users can read quality at a glance.
 */
function renderDistributionBar(counts) {
    const segments = [
        ["good", counts.good],
        ["redirected", counts.redirected],
        ["broken", counts.broken],
        ["error", counts.error],
    ];

    distributionBar.innerHTML = "";

    if (!counts.total) {
        distributionBar.innerHTML = '<span class="distribution-empty"></span>';

        return;
    }

    segments.forEach(([name, count]) => {
        if (!count) {
            return;
        }

        const segment = document.createElement("span");
        const percent = Math.max((count / counts.total) * 100, 3);

        segment.className = `distribution-segment distribution-${name}`;
        segment.style.width = `${percent}%`;
        segment.title = `${count} ${name}`;

        distributionBar.appendChild(segment);
    });
}


/**
 * Render the most important actionable rows above the full table.
 */
function renderIssues(results) {
    const issueResults = results
        .filter(needsAction)
        .slice(0, 6);

    const totalIssues = results.filter(needsAction).length;

    issuesSubtitleElement.textContent = totalIssues === 0
        ? "No broken links or request errors were detected."
        : `${totalIssues} links require attention.`;

    issuesList.innerHTML = "";

    if (issueResults.length === 0) {
        issuesList.innerHTML = `
            <div class="issue-empty">
                No priority issues in this scan.
            </div>
        `;

        return;
    }

    issueResults.forEach((result) => {
        const statusGroup = getStatusGroup(result);
        const statusLabel = getStatusLabel(statusGroup, result.status);
        const issueItem = document.createElement("article");
        const detail = result.error_description ||
            result.error_message ||
            result.source_location ||
            "No additional details provided.";

        issueItem.className = "issue-item";
        issueItem.innerHTML = `
            <div>
                <span class="status-badge status-${statusGroup}">
                    ${escapeHtml(statusLabel)}
                </span>
            </div>

            <div class="issue-content">
                <strong>${escapeHtml(result.url || "Unknown URL")}</strong>
                <p>${escapeHtml(detail)}</p>
            </div>

            <div class="issue-meta">
                ${escapeHtml(result.http_status ?? result.link_type ?? "-")}
            </div>
        `;

        issuesList.appendChild(issueItem);
    });
}


/**
 * Render the scan results table.
 */
function renderTable(results) {
    resultsTableBody.innerHTML = "";

    updateSortButtons();

    const filteredResults = getVisibleResults(results);

    if (filteredResults.length === 0) {
        resultsTableBody.innerHTML = `
            <tr>
                <td colspan="10" class="empty-state">
                    No links found for the selected filter.
                </td>
            </tr>
        `;

        return;
    }

    filteredResults.forEach((result) => {
        const statusGroup = getStatusGroup(result);

        const statusLabel = getStatusLabel(statusGroup, result.status);

        const responseTime = result.response_time_ms !== null &&
            result.response_time_ms !== undefined
            ? `${result.response_time_ms} ms`
            : "-";
        const redirectChain = formatRedirectChain(result.redirect_chain);

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>
                <span class="status-badge status-${statusGroup}">
                    ${escapeHtml(statusLabel)}
                </span>
            </td>

            <td>
                ${escapeHtml(result.http_status ?? "-")}
            </td>

            <td class="url-cell">
                ${renderUrlCell(result.url, "link URL")}
            </td>

            <td class="url-cell">
                ${renderUrlCell(result.final_url, "final URL")}
            </td>

            <td>
                ${escapeHtml(redirectChain || "-")}
            </td>

            <td>
                ${escapeHtml(responseTime)}
            </td>

            <td class="url-cell">
                ${escapeHtml(result.source_location ?? "-")}
            </td>

            <td>
                ${escapeHtml(result.link_type ?? "-")}
            </td>

            <td>
                ${escapeHtml(result.source_attribute ?? "-")}
            </td>

            <td class="url-cell">
                ${renderCopyableValue(result.error_message, "error message")}
            </td>
        `;

        resultsTableBody.appendChild(row);
    });
}


function showScanData(scanData) {
    currentResults = scanData.results ?? [];
    currentSourcePage = scanData.source_page ?? "";

    statusFilter.value = "all";
    resultsSearchInput.value = "";
    currentSort = {
        key: null,
        direction: "asc",
    };
    quickFilter = "all";
    needsActionFilterButton.dataset.active = "false";

    renderSummary(scanData);
    renderIssues(currentResults);
    renderTable(currentResults);

    emptySection.classList.add("hidden");
    resultsSection.classList.remove("hidden");
}


function setHistoryCollapsed(isCollapsed) {
    historyPanel.dataset.collapsed = isCollapsed ? "true" : "false";
    historyList.classList.toggle("hidden", isCollapsed);
    toggleHistoryButton.textContent = isCollapsed ? "Expand" : "Minimize";
    toggleHistoryButton.setAttribute("aria-expanded", isCollapsed ? "false" : "true");
}


function setIssuesCollapsed(isCollapsed) {
    const issuesPanel = issuesList.closest(".issues-panel");

    issuesPanel.dataset.collapsed = isCollapsed ? "true" : "false";
    issuesList.classList.toggle("hidden", isCollapsed);
    toggleIssuesButton.textContent = isCollapsed ? "Expand" : "Minimize";
    toggleIssuesButton.setAttribute("aria-expanded", isCollapsed ? "false" : "true");
}


function renderScanHistory(history) {
    historyList.innerHTML = "";

    if (!Array.isArray(history) || history.length === 0) {
        historySubtitle.textContent = "Recent local scans saved on this machine.";
        historyList.innerHTML = '<div class="history-empty">No saved scans yet.</div>';

        return;
    }

    historySubtitle.textContent = `${history.length} scans saved locally.`;

    history.forEach((item) => {
        const historyItem = document.createElement("button");
        const issueCount = (item.broken ?? 0) + (item.error ?? 0);

        historyItem.className = "history-item";
        historyItem.type = "button";
        historyItem.dataset.scanId = item.id;
        historyItem.dataset.active = item.id === selectedHistoryScanId
            ? "true"
            : "false";
        historyItem.innerHTML = `
            <span>
                <span class="history-url">${escapeHtml(item.source_page ?? "Unknown page")}</span>
                <span class="history-meta">${escapeHtml(formatHistoryDate(item.created_at))}</span>
            </span>

            <span class="history-counts">
                ${escapeHtml(item.total_links ?? 0)} links | ${escapeHtml(issueCount)} issues
            </span>
        `;

        historyList.appendChild(historyItem);
    });
}


async function loadScanHistory() {
    try {
        const response = await fetch("/scans/history");

        if (!response.ok) {
            throw new Error("History could not be loaded.");
        }

        renderScanHistory(await response.json());
    } catch {
        historySubtitle.textContent = "History is unavailable.";
        historyList.innerHTML = '<div class="history-empty">Could not load local scan history.</div>';
    }
}


async function loadHistoryScan(scanId) {
    const response = await fetch(`/scans/history/${encodeURIComponent(scanId)}`);

    if (!response.ok) {
        throw new Error("The selected scan could not be loaded.");
    }

    return response.json();
}


/**
 * Send the page URL to the FastAPI scan endpoint.
 */
async function executeScan(pageUrl) {
    const response = await fetch("/scans", {
        method: "POST",

        headers: {
            "Content-Type": "application/json",
        },

        body: JSON.stringify({
            url: pageUrl,
        }),
    });

    if (!response.ok) {
        let errorMessage = "The scan could not be completed.";

        try {
            const errorData = await response.json();

            errorMessage =
                errorData.detail ||
                errorData.message ||
                errorMessage;
        } catch {
            // Keep the default error message when the response is not JSON.
        }

        throw new Error(errorMessage);
    }

    return response.json();
}


async function refreshCurrentScanOrHistory() {
    const pageUrl = currentSourcePage || pageUrlInput.value.trim();

    formError.classList.add("hidden");
    refreshHistoryButton.disabled = true;

    if (!pageUrl) {
        refreshHistoryButton.textContent = "Refreshing...";
        setAppStatus("scanning", "Refreshing");

        try {
            await loadScanHistory();
            setAppStatus("ready", "Ready");
        } catch {
            setAppStatus("error", "Error");
        } finally {
            refreshHistoryButton.disabled = false;
            refreshHistoryButton.textContent = "Refresh";
        }

        return;
    }

    emptySection.classList.add("hidden");
    resultsSection.classList.add("hidden");
    loadingSection.classList.remove("hidden");
    loadingUrlElement.textContent = pageUrl;
    refreshHistoryButton.textContent = "Refreshing...";
    scanButton.disabled = true;
    setAppStatus("scanning", "Refreshing");

    try {
        const scanData = await executeScan(pageUrl);

        selectedHistoryScanId = "";
        showScanData(scanData);
        await loadScanHistory();
        setAppStatus("ready", "Ready");
    } catch (error) {
        formError.textContent =
            error.message ||
            "An unexpected error occurred.";

        formError.classList.remove("hidden");
        resultsSection.classList.toggle("hidden", currentResults.length === 0);
        emptySection.classList.toggle("hidden", currentResults.length > 0);
        setAppStatus("error", "Error");
    } finally {
        loadingSection.classList.add("hidden");
        refreshHistoryButton.disabled = false;
        refreshHistoryButton.textContent = "Refresh";
        scanButton.disabled = false;
        scanButton.textContent = "Analyze";
    }
}


/**
 * Handle form submission without reloading the browser page.
 */
scanForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const pageUrl = pageUrlInput.value.trim();

    formError.classList.add("hidden");
    emptySection.classList.add("hidden");
    resultsSection.classList.add("hidden");
    loadingSection.classList.remove("hidden");
    loadingUrlElement.textContent = pageUrl;

    scanButton.disabled = true;
    scanButton.textContent = "Analyzing...";
    setAppStatus("scanning", "Scanning");

    try {
        const scanData = await executeScan(pageUrl);

        selectedHistoryScanId = "";
        showScanData(scanData);
        await loadScanHistory();
        setAppStatus("ready", "Ready");
    } catch (error) {
        formError.textContent =
            error.message ||
            "An unexpected error occurred.";

        formError.classList.remove("hidden");
        emptySection.classList.remove("hidden");
        setAppStatus("error", "Error");
    } finally {
        loadingSection.classList.add("hidden");

        scanButton.disabled = false;
        scanButton.textContent = "Analyze";
    }
});


refreshHistoryButton.addEventListener("click", refreshCurrentScanOrHistory);


toggleHistoryButton.addEventListener("click", () => {
    setHistoryCollapsed(historyPanel.dataset.collapsed !== "true");
});


toggleIssuesButton.addEventListener("click", () => {
    const issuesPanel = issuesList.closest(".issues-panel");

    setIssuesCollapsed(issuesPanel.dataset.collapsed !== "true");
});


historyList.addEventListener("click", async (event) => {
    const historyItem = event.target.closest(".history-item");

    if (!historyItem) {
        return;
    }

    formError.classList.add("hidden");
    setAppStatus("scanning", "Loading");

    try {
        const scanData = await loadHistoryScan(historyItem.dataset.scanId);

        selectedHistoryScanId = historyItem.dataset.scanId;
        showScanData(scanData);
        await loadScanHistory();
        setAppStatus("ready", "Ready");
    } catch (error) {
        formError.textContent = error.message;
        formError.classList.remove("hidden");
        setAppStatus("error", "Error");
    }
});


/**
 * Filter the existing results without executing a new scan.
 */
statusFilter.addEventListener("change", () => {
    quickFilter = "all";
    needsActionFilterButton.dataset.active = "false";
    renderTable(currentResults);
});


/**
 * Search within the current scan results.
 */
resultsSearchInput.addEventListener("input", () => {
    renderTable(currentResults);
});


/**
 * Focus the table on broken links and request errors.
 */
needsActionFilterButton.addEventListener("click", () => {
    quickFilter = quickFilter === "needs-action"
        ? "all"
        : "needs-action";

    statusFilter.value = "all";
    needsActionFilterButton.dataset.active = quickFilter === "needs-action"
        ? "true"
        : "false";
    renderTable(currentResults);
});


/**
 * Sort the table by a selected column.
 */
document.querySelectorAll(".sort-button").forEach((button) => {
    button.addEventListener("click", () => {
        const sortKey = button.dataset.sortKey;

        if (currentSort.key === sortKey) {
            currentSort.direction = currentSort.direction === "asc"
                ? "desc"
                : "asc";
        } else {
            currentSort = {
                key: sortKey,
                direction: "asc",
            };
        }

        renderTable(currentResults);
    });
});


/**
 * Export the visible result set as a CSV file.
 */
exportCsvButton.addEventListener("click", exportCurrentResultsToCsv);


/**
 * Copy result URLs without re-rendering the table.
 */
resultsTableBody.addEventListener("click", async (event) => {
    const copyButton = event.target.closest(".copy-button");

    if (!copyButton) {
        return;
    }

    const valueToCopy = copyButton.dataset.copy;

    if (!valueToCopy) {
        return;
    }

    try {
        await navigator.clipboard.writeText(valueToCopy);

        const originalText = copyButton.textContent;

        copyButton.textContent = "Copied";
        copyButton.disabled = true;

        window.setTimeout(() => {
            copyButton.textContent = originalText;
            copyButton.disabled = false;
        }, 1200);
    } catch {
        formError.textContent = "The URL could not be copied.";
        formError.classList.remove("hidden");
    }
});


loadScanHistory();
