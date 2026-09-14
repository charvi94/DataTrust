let map = null;

let currentIssues = [];

let issueDistributionChart = null;
let qualityScoreChart = null;
let cityDistributionChart = null;
let cleaningImpactChart = null;


// ============================================================
// ELEMENTS
// ============================================================

const fileInput =
    document.getElementById("fileInput");

const analyzeButton =
    document.getElementById("analyzeButton");

const cleanButton =
    document.getElementById("cleanButton");

const status =
    document.getElementById("status");

const issueFilter =
    document.getElementById("issueFilter");

const clearIssueFilter =
    document.getElementById(
        "clearIssueFilter"
    );


// ============================================================
// SAFE DISPLAY
// ============================================================

function displayValue(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }

    return String(value);
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(value) {

    return displayValue(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ============================================================
// ANALYZE DATASET
// ============================================================

analyzeButton.addEventListener(
    "click",
    async () => {

        const file =
            fileInput.files[0];


        if (!file) {

            status.textContent =
                "Please select a CSV file.";

            return;
        }


        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        status.textContent =
            "Analyzing dataset...";


        try {

            const response =
                await fetch(
                    "/api/upload",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            console.log(
                "API response:",
                data
            );


            if (!response.ok) {

                status.textContent =
                    data.error ||
                    "Analysis failed.";

                return;
            }


            // =================================================
            // VALIDATION
            // =================================================

            const validation =
                data.validation || {};


            const totalRecords =
                Number(
                    validation.total_records ?? 0
                );


            const missingValues =
                Number(
                    validation.missing_values ?? 0
                );


            const invalidEmails =
                Number(
                    validation.invalid_emails ?? 0
                );


            const invalidPhones =
                Number(
                    validation.invalid_phones ?? 0
                );


            const duplicateRecords =
                Number(
                    data.duplicate_records ?? 0
                );


            // =================================================
            // RESULT CARDS
            // =================================================

            document.getElementById(
                "totalRecords"
            ).textContent =
                totalRecords;


            document.getElementById(
                "missingValues"
            ).textContent =
                missingValues;


            document.getElementById(
                "invalidEmails"
            ).textContent =
                invalidEmails;


            document.getElementById(
                "invalidPhones"
            ).textContent =
                invalidPhones;


            document.getElementById(
                "duplicateRecords"
            ).textContent =
                duplicateRecords;


            // =================================================
            // QUALITY SCORE
            // =================================================

            const score =
                Number(
                    data.quality_score ?? 0
                );


            document.getElementById(
                "qualityScore"
            ).textContent =
                score.toFixed(2);


            const qualityLabel =
                document.getElementById(
                    "qualityLabel"
                );


            if (score >= 80) {

                qualityLabel.textContent =
                    "Excellent Quality";

            }
            else if (score >= 60) {

                qualityLabel.textContent =
                    "Good Quality";

            }
            else if (score >= 40) {

                qualityLabel.textContent =
                    "Needs Improvement";

            }
            else {

                qualityLabel.textContent =
                    "Poor Quality";
            }


            // =================================================
            // BASIC ISSUE COUNTS
            // =================================================

            document.getElementById(
                "issueMissing"
            ).textContent =
                missingValues;


            document.getElementById(
                "issueEmails"
            ).textContent =
                invalidEmails;


            document.getElementById(
                "issuePhones"
            ).textContent =
                invalidPhones;


            document.getElementById(
                "issueDuplicates"
            ).textContent =
                duplicateRecords;


            // =================================================
            // ISSUE MANAGEMENT
            // =================================================

            currentIssues =
                Array.isArray(data.issues)
                    ? data.issues
                    : [];


            updateIssueSummary(
                data.issue_summary
            );


            renderIssues(
                currentIssues
            );


            // =================================================
            // DUPLICATES
            // =================================================

            renderDuplicates(
                data.duplicates || []
            );


            // =================================================
            // MAP
            // =================================================

            renderMap(
                data.locations || []
            );


            // =================================================
            // CHARTS
            // =================================================

            renderIssueDistributionChart(
                missingValues,
                invalidEmails,
                invalidPhones,
                duplicateRecords
            );


            renderQualityScoreChart(
                score
            );


            renderCityDistributionChart(
                data.locations || []
            );


            status.textContent =
                "Analysis completed successfully.";

        }
        catch (error) {

            console.error(
                "FULL ANALYSIS ERROR:",
                error
            );


            status.textContent =
                "ERROR: " +
                error.message;
        }

    }
);


// ============================================================
// ISSUE SUMMARY
// ============================================================

function updateIssueSummary(
    summary
) {

    summary =
        summary || {};


    document.getElementById(
        "totalIssues"
    ).textContent =
        displayValue(
            summary.total ??
            currentIssues.length
        );


    document.getElementById(
        "summaryMissing"
    ).textContent =
        displayValue(
            summary.missing_values ?? 0
        );


    document.getElementById(
        "summaryEmails"
    ).textContent =
        displayValue(
            summary.invalid_emails ?? 0
        );


    document.getElementById(
        "summaryPhones"
    ).textContent =
        displayValue(
            summary.invalid_phones ?? 0
        );


    document.getElementById(
        "summaryDuplicates"
    ).textContent =
        displayValue(
            summary.duplicates ?? 0
        );
}


// ============================================================
// ISSUE TABLE
// ============================================================

function renderIssues(
    issues
) {

    const tableBody =
        document.getElementById(
            "issuesTableBody"
        );


    tableBody.innerHTML = "";


    if (
        !Array.isArray(issues) ||
        issues.length === 0
    ) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="7">
                    No data-quality issues detected.
                </td>
            </tr>
        `;

        return;
    }


    issues.forEach(
        (issue, index) => {

            const row =
                document.createElement(
                    "tr"
                );


            const severity =
                displayValue(
                    issue.severity ||
                    "Medium"
                );


            row.innerHTML = `

                <td>
                    ${escapeHtml(
                        issue.record_index ??
                        index
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        issue.customer_id
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        issue.issue_type
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        issue.field
                    )}
                </td>

                <td>
                    <strong>
                        ${escapeHtml(
                            severity
                        )}
                    </strong>
                </td>

                <td>
                    ${escapeHtml(
                        issue.description
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        issue.suggestion
                    )}
                </td>

            `;


            tableBody.appendChild(
                row
            );

        }
    );
}


// ============================================================
// ISSUE FILTER
// ============================================================

issueFilter.addEventListener(
    "change",
    () => {

        const selected =
            issueFilter.value;


        if (
            selected === "all"
        ) {

            renderIssues(
                currentIssues
            );

            return;
        }


        const filtered =
            currentIssues.filter(
                issue =>
                    issue.issue_type ===
                    selected
            );


        renderIssues(
            filtered
        );

    }
);


// ============================================================
// CLEAR FILTER
// ============================================================

clearIssueFilter.addEventListener(
    "click",
    () => {

        issueFilter.value =
            "all";


        renderIssues(
            currentIssues
        );

    }
);


// ============================================================
// DUPLICATE TABLE
// ============================================================

function renderDuplicates(
    duplicates
) {

    const tableBody =
        document.getElementById(
            "duplicatesTableBody"
        );


    tableBody.innerHTML = "";


    if (
        !Array.isArray(duplicates) ||
        duplicates.length === 0
    ) {

        tableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    No duplicates found
                </td>
            </tr>
        `;

        return;
    }


    duplicates.forEach(
        record => {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${escapeHtml(
                        record.customer_id
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        record.name
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        record.email
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        record.phone
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        record.city
                    )}
                </td>

            `;


            tableBody.appendChild(
                row
            );

        }
    );
}


// ============================================================
// MAP
// ============================================================

function renderMap(
    locations
) {

    if (map === null) {

        map =
            L.map(
                "map"
            ).setView(
                [
                    20.5937,
                    78.9629
                ],
                5
            );


        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                attribution:
                    "&copy; OpenStreetMap contributors"
            }
        ).addTo(
            map
        );
    }


    map.eachLayer(
        layer => {

            if (
                layer instanceof L.Marker
            ) {

                map.removeLayer(
                    layer
                );
            }

        }
    );


    const mapPoints = [];


    locations.forEach(
        location => {

            const latitude =
                Number(
                    location.latitude
                );


            const longitude =
                Number(
                    location.longitude
                );


            if (
                Number.isNaN(latitude) ||
                Number.isNaN(longitude)
            ) {

                return;
            }


            const marker =
                L.marker(
                    [
                        latitude,
                        longitude
                    ]
                ).addTo(
                    map
                );


            marker.bindPopup(`

                <strong>
                    ${escapeHtml(
                        location.name
                    )}
                </strong>

                <br>

                Customer ID:
                ${escapeHtml(
                    location.customer_id
                )}

                <br>

                City:
                ${escapeHtml(
                    location.city
                )}

            `);


            mapPoints.push(
                [
                    latitude,
                    longitude
                ]
            );

        }
    );


    if (
        mapPoints.length > 0
    ) {

        const bounds =
            L.latLngBounds(
                mapPoints
            );


        map.fitBounds(
            bounds,
            {
                padding: [
                    30,
                    30
                ]
            }
        );
    }
}


// ============================================================
// CHART 1 — ISSUE DISTRIBUTION
// ============================================================

function renderIssueDistributionChart(
    missing,
    emails,
    phones,
    duplicates
) {

    const canvas =
        document.getElementById(
            "issueDistributionChart"
        );


    if (!canvas) {
        return;
    }


    if (
        issueDistributionChart
    ) {

        issueDistributionChart.destroy();
    }


    issueDistributionChart =
        new Chart(
            canvas,
            {
                type: "bar",

                data: {

                    labels: [
                        "Missing Values",
                        "Invalid Emails",
                        "Invalid Phones",
                        "Duplicates"
                    ],

                    datasets: [
                        {
                            label:
                                "Number of Issues",

                            data: [
                                missing,
                                emails,
                                phones,
                                duplicates
                            ]
                        }
                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,

                    plugins: {

                        legend: {
                            display: false
                        }

                    },

                    scales: {

                        y: {

                            beginAtZero:
                                true,

                            ticks: {
                                precision: 0
                            }

                        }

                    }

                }

            }
        );
}


// ============================================================
// CHART 2 — QUALITY SCORE
// ============================================================

function renderQualityScoreChart(
    score
) {

    const canvas =
        document.getElementById(
            "qualityScoreChart"
        );


    if (!canvas) {
        return;
    }


    if (
        qualityScoreChart
    ) {

        qualityScoreChart.destroy();
    }


    const remaining =
        Math.max(
            0,
            100 - score
        );


    qualityScoreChart =
        new Chart(
            canvas,
            {
                type: "doughnut",

                data: {

                    labels: [
                        "Quality Score",
                        "Remaining"
                    ],

                    datasets: [
                        {
                            data: [
                                score,
                                remaining
                            ]
                        }
                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,

                    cutout:
                        "70%",

                    plugins: {

                        legend: {
                            position: "bottom"
                        }

                    }

                }

            }
        );
}


// ============================================================
// CHART 3 — CITY DISTRIBUTION
// ============================================================

function renderCityDistributionChart(
    locations
) {

    const canvas =
        document.getElementById(
            "cityDistributionChart"
        );


    if (!canvas) {
        return;
    }


    if (
        cityDistributionChart
    ) {

        cityDistributionChart.destroy();
    }


    const cityCounts = {};


    locations.forEach(
        location => {

            const city =
                displayValue(
                    location.city
                ).trim();


            if (!city) {
                return;
            }


            cityCounts[city] =
                (
                    cityCounts[city] ||
                    0
                ) + 1;

        }
    );


    const cities =
        Object.keys(
            cityCounts
        );


    const counts =
        cities.map(
            city =>
                cityCounts[city]
        );


    cityDistributionChart =
        new Chart(
            canvas,
            {
                type: "bar",

                data: {

                    labels: cities,

                    datasets: [
                        {
                            label:
                                "Records",

                            data: counts
                        }
                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,

                    plugins: {

                        legend: {
                            display: false
                        }

                    },

                    scales: {

                        y: {

                            beginAtZero:
                                true,

                            ticks: {
                                precision: 0
                            }

                        }

                    }

                }

            }
        );
}


// ============================================================
// CLEAN DATASET
// ============================================================

cleanButton.addEventListener(
    "click",
    async () => {

        const file =
            fileInput.files[0];


        if (!file) {

            status.textContent =
                "Please select a CSV file.";

            return;
        }


        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        status.textContent =
            "Cleaning and standardizing dataset...";


        try {

            const response =
                await fetch(
                    "/api/clean",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            console.log(
                "Clean API response:",
                data
            );


            if (!response.ok) {

                status.textContent =
                    data.error ||
                    "Cleaning failed.";

                return;
            }


            const summary =
                data.cleaning_summary ||
                data.cleaning ||
                {};


            const beforeRecords =
                Number(
                    data.before_records ??
                    summary.before_records ??
                    data.records_processed ??
                    summary.records_processed ??
                    0
                );


            const afterRecords =
                Number(
                    data.after_records ??
                    summary.after_records ??
                    data.data?.length ??
                    0
                );


            const recordsChanged =
                Number(
                    data.records_changed ??
                    summary.records_changed ??
                    0
                );


            document.getElementById(
                "recordsProcessed"
            ).textContent =
                beforeRecords;


            document.getElementById(
                "namesStandardized"
            ).textContent =
                data.names_standardized ??
                summary.names_standardized ??
                0;


            document.getElementById(
                "emailsStandardized"
            ).textContent =
                data.emails_standardized ??
                summary.emails_standardized ??
                0;


            document.getElementById(
                "phonesStandardized"
            ).textContent =
                data.phones_standardized ??
                summary.phones_standardized ??
                0;


            document.getElementById(
                "citiesStandardized"
            ).textContent =
                data.cities_standardized ??
                summary.cities_standardized ??
                0;


            document.getElementById(
                "originalRecords"
            ).textContent =
                beforeRecords;


            document.getElementById(
                "cleanedRecords"
            ).textContent =
                afterRecords;


            document.getElementById(
                "recordsChanged"
            ).textContent =
                recordsChanged;


            document.getElementById(
                "cleaningStatus"
            ).textContent =
                summary.status ||
                "Completed";


            renderCleaningPreview(
                data.preview || []
            );


            renderCleanedDataset(
                data.data || []
            );


            createDownloadButton(
                data.cleaned_filename ||
                (
                    "cleaned_" +
                    (
                        data.filename ||
                        file.name
                    )
                )
            );


            // =================================================
            // CLEANING IMPACT CHART
            // =================================================

            renderCleaningImpactChart(
                beforeRecords,
                afterRecords,
                recordsChanged
            );


            status.textContent =
                "Dataset cleaned and standardized successfully.";

        }
        catch (error) {

            console.error(
                "FULL CLEANING ERROR:",
                error
            );


            status.textContent =
                "ERROR: " +
                error.message;
        }

    }
);


// ============================================================
// CHART 4 — CLEANING IMPACT
// ============================================================

function renderCleaningImpactChart(
    before,
    after,
    changed
) {

    const canvas =
        document.getElementById(
            "cleaningImpactChart"
        );


    if (!canvas) {
        return;
    }


    if (
        cleaningImpactChart
    ) {

        cleaningImpactChart.destroy();
    }


    cleaningImpactChart =
        new Chart(
            canvas,
            {
                type: "bar",

                data: {

                    labels: [
                        "Original Records",
                        "Cleaned Records",
                        "Modified Records"
                    ],

                    datasets: [
                        {
                            label:
                                "Records",

                            data: [
                                before,
                                after,
                                changed
                            ]
                        }
                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,

                    plugins: {

                        legend: {
                            display: false
                        }

                    },

                    scales: {

                        y: {

                            beginAtZero:
                                true,

                            ticks: {
                                precision: 0
                            }

                        }

                    }

                }

            }
        );
}


// ============================================================
// CLEANING PREVIEW
// ============================================================

function renderCleaningPreview(
    preview
) {

    const body =
        document.getElementById(
            "cleaningPreviewBody"
        );


    body.innerHTML = "";


    if (
        !Array.isArray(preview) ||
        preview.length === 0
    ) {

        body.innerHTML = `
            <tr>
                <td colspan="3">
                    No values were changed.
                </td>
            </tr>
        `;

        return;
    }


    preview.forEach(
        item => {

            const row =
                document.createElement(
                    "tr"
                );


            row.innerHTML = `

                <td>
                    ${escapeHtml(
                        item.field
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        item.before
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        item.after
                    )}
                </td>

            `;


            body.appendChild(
                row
            );

        }
    );
}


// ============================================================
// CLEANED DATASET TABLE
// ============================================================

function renderCleanedDataset(
    records
) {

    const head =
        document.getElementById(
            "cleanedTableHead"
        );


    const body =
        document.getElementById(
            "cleanedTableBody"
        );


    head.innerHTML = "";

    body.innerHTML = "";


    if (
        !Array.isArray(records) ||
        records.length === 0
    ) {

        body.innerHTML = `
            <tr>
                <td>
                    No cleaned records available.
                </td>
            </tr>
        `;

        return;
    }


    const headers =
        Object.keys(
            records[0]
        );


    const headerRow =
        document.createElement(
            "tr"
        );


    headers.forEach(
        header => {

            const th =
                document.createElement(
                    "th"
                );


            th.textContent =
                header;


            headerRow.appendChild(
                th
            );

        }
    );


    head.appendChild(
        headerRow
    );


    records.forEach(
        record => {

            const row =
                document.createElement(
                    "tr"
                );


            headers.forEach(
                header => {

                    const td =
                        document.createElement(
                            "td"
                        );


                    td.textContent =
                        displayValue(
                            record[header]
                        );


                    row.appendChild(
                        td
                    );

                }
            );


            body.appendChild(
                row
            );

        }
    );
}


// ============================================================
// DOWNLOAD
// ============================================================

function createDownloadButton(
    filename
) {

    const container =
        document.getElementById(
            "downloadContainer"
        );


    container.innerHTML = "";


    const button =
        document.createElement(
            "a"
        );


    button.href =
        "/api/download/" +
        encodeURIComponent(
            filename
        );


    button.textContent =
        "Download Cleaned Dataset";


    button.className =
        "download-button";


    button.download =
        filename;


    container.appendChild(
        button
    );
}