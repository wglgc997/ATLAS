const scanForm = document.getElementById("scan-form");
const pageUrlInput = document.getElementById("page-url");
const scanButton = document.getElementById("scan-button");
const formError = document.getElementById("form-error");
const appStatus = document.getElementById("app-status");
const appStatusText = document.getElementById("app-status-text");

const emptySection = document.getElementById("empty-section");
const loadingSection = document.getElementById("loading-section");
const loadingUrlElement = document.getElementById("loading-url");
const resultsSection = document.getElementById("results-section");

const totalLinksElement = document.getElementById("total-links");
const goodLinksElement = document.getElementById("good-links");
const redirectedLinksElement = document.getElementById("redirected-links");
const brokenLinksElement = document.getElementById("broken-links");
const errorLinksElement = document.getElementById("error-links");

const sourcePageElement = document.getElementById("source-page");
const resultsTableBody = document.getElementById("results-table-body");
const resultsSearchInput = document.getElementById("results-search");
const statusFilter = document.getElementById("status-filter");
const exportCsvButton = document.getElementById("export-csv-button");

let currentResults = [];
let currentSourcePage = "";
let currentSort = {
    key: null,
    direction: "asc",
};


/**
 * Update the compact status indicator in the app header.
 */
function setAppStatus(status, label) {
    appStatus.dataset.status = status;
    appStatusText.textContent = label;
}


/**
 * Normalize the API status so the frontend can apply
 * consistent styles and filters.
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
        normalizedStatus === "valid"
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
        normalizedStatus === "failed"
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


/**
 * Convert the internal status value into readable text.
 */
function getStatusLabel(status, rawStatus = null) {
    const labels = {
        good: "Valid",
        redirected: "Redirected",
        broken: "Broken",
        error: rawStatus || "Error",
        unknown: "Unknown",
    };

    return labels[status] || labels.unknown;
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
        return getStatusLabel(normalizeStatus(result.status), result.status)
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
        const normalizedStatus = normalizeStatus(result.status);
        const matchesStatus = (
            selectedStatus === "all" ||
            normalizedStatus === selectedStatus
        );

        const matchesSearch = (
            searchTerm === "" ||
            getSearchableText(result).includes(searchTerm)
        );

        return matchesStatus && matchesSearch;
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
        "response_time_ms",
        "source_location",
        "link_type",
        "source_attribute",
        "error_message",
    ];

    const rows = filteredResults.map((result) => [
        currentSourcePage,
        getStatusLabel(normalizeStatus(result.status), result.status),
        result.http_status ?? "",
        result.url ?? "",
        result.final_url ?? "",
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

    totalLinksElement.textContent = data.total_links ?? 0;
    goodLinksElement.textContent = data.good ?? 0;
    redirectedLinksElement.textContent = data.redirected ?? 0;
    brokenLinksElement.textContent = data.broken ?? 0;
    errorLinksElement.textContent = data.error ?? 0;

    sourcePageElement.textContent = data.source_page
        ? `Source page: ${data.source_page}`
        : "";
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
                <td colspan="9" class="empty-state">
                    No links found for the selected filter.
                </td>
            </tr>
        `;

        return;
    }

    filteredResults.forEach((result) => {
        const normalizedStatus = normalizeStatus(result.status);

        const statusLabel = getStatusLabel(normalizedStatus, result.status);

        const responseTime = result.response_time_ms !== null &&
            result.response_time_ms !== undefined
            ? `${result.response_time_ms} ms`
            : "-";

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>
                <span class="status-badge status-${normalizedStatus}">
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

        currentResults = scanData.results ?? [];

        statusFilter.value = "all";
        resultsSearchInput.value = "";
        currentSort = {
            key: null,
            direction: "asc",
        };

        renderSummary(scanData);
        renderTable(currentResults);

        resultsSection.classList.remove("hidden");
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


/**
 * Filter the existing results without executing a new scan.
 */
statusFilter.addEventListener("change", () => {
    renderTable(currentResults);
});


/**
 * Search within the current scan results.
 */
resultsSearchInput.addEventListener("input", () => {
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
