const scanForm = document.getElementById("scan-form");
const pageUrlInput = document.getElementById("page-url");
const scanButton = document.getElementById("scan-button");
const formError = document.getElementById("form-error");

const loadingSection = document.getElementById("loading-section");
const resultsSection = document.getElementById("results-section");

const totalLinksElement = document.getElementById("total-links");
const goodLinksElement = document.getElementById("good-links");
const redirectedLinksElement = document.getElementById("redirected-links");
const brokenLinksElement = document.getElementById("broken-links");
const errorLinksElement = document.getElementById("error-links");

const sourcePageElement = document.getElementById("source-page");
const resultsTableBody = document.getElementById("results-table-body");
const statusFilter = document.getElementById("status-filter");

let currentResults = [];


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

    if (normalizedStatus === "error") {
        return "error";
    }

    return "unknown";
}


/**
 * Convert the internal status value into readable text.
 */
function getStatusLabel(status) {
    const labels = {
        good: "Valid",
        redirected: "Redirected",
        broken: "Broken",
        error: "Error",
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
 * Render the scan summary cards.
 */
function renderSummary(data) {
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
function renderTable(results, selectedStatus = "all") {
    resultsTableBody.innerHTML = "";

    const filteredResults = results.filter((result) => {
        const normalizedStatus = normalizeStatus(result.status);

        return (
            selectedStatus === "all" ||
            normalizedStatus === selectedStatus
        );
    });

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

        const statusLabel = getStatusLabel(normalizedStatus);

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
                ${escapeHtml(result.url ?? "-")}
            </td>

            <td class="url-cell">
                ${escapeHtml(result.final_url ?? "-")}
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
                ${escapeHtml(result.error_message ?? "-")}
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
    resultsSection.classList.add("hidden");
    loadingSection.classList.remove("hidden");

    scanButton.disabled = true;
    scanButton.textContent = "Analyzing...";

    try {
        const scanData = await executeScan(pageUrl);

        currentResults = scanData.results ?? [];

        renderSummary(scanData);
        renderTable(currentResults);

        statusFilter.value = "all";
        resultsSection.classList.remove("hidden");
    } catch (error) {
        formError.textContent =
            error.message ||
            "An unexpected error occurred.";

        formError.classList.remove("hidden");
    } finally {
        loadingSection.classList.add("hidden");

        scanButton.disabled = false;
        scanButton.textContent = "Analyze links";
    }
});


/**
 * Filter the existing results without executing a new scan.
 */
statusFilter.addEventListener("change", () => {
    renderTable(currentResults, statusFilter.value);
});
