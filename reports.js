/* =========================================
   METRISCAN REPORTS
   reports.js
========================================= */


/* =================================================
   DEMONSTRATION REPORT DATA
================================================= */

/*
    These are temporary frontend records.

    Later:
    OCR → Compliance Engine → Backend → Database
    will provide real report data.
*/
// =========================
// APPLY SAVED THEME
// =========================

function applySavedTheme() {
    const savedSettings =
        JSON.parse(localStorage.getItem("metriscanSettings")) || {};

    const theme = savedSettings.theme || "dark";

    if (theme === "light") {
        document.body.classList.add("light-theme");
    } else {
        document.body.classList.remove("light-theme");
    }
}

applySavedTheme();

const reportsData = [

    {
        id: "RPT-001",

        productName:
            "PureWash Detergent Powder",

        manufacturer:
            "ABC Consumer Products Pvt. Ltd.",

        quantity:
            "1 kg",

        mrp:
            "₹145",

        country:
            "India",

        date:
            "12 Sep 2026",

        time:
            "10:42 AM",

        status:
            "compliant",

        statusText:
            "Compliant",

        passed:
            12,

        total:
            12,

        checks: [

            {
                name:
                    "Manufacturer Name & Address",

                value:
                    "ABC Consumer Products Pvt. Ltd.",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "Common / Generic Name",

                value:
                    "Detergent Powder",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "Net Quantity",

                value:
                    "1 kg",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "MRP / Retail Sale Price",

                value:
                    "MRP ₹145",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "Consumer Care Details",

                value:
                    "1800-123-4567",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "Manufacturing Date",

                value:
                    "08/2026",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            }

        ],

        issue:
            "",

        ruleReference:
            "Applicable Legal Metrology packaged-commodity declaration requirements were satisfied for the verified fields."

    },


    {
        id: "RPT-002",

        productName:
            "FreshGlow Face Wash",

        manufacturer:
            "GlowCare Industries",

        quantity:
            "100 ml",

        mrp:
            "₹99",

        country:
            "India",

        date:
            "11 Sep 2026",

        time:
            "03:18 PM",

        status:
            "non-compliant",

        statusText:
            "Non-Compliant",

        passed:
            9,

        total:
            12,

        checks: [

            {
                name:
                    "Manufacturer Name & Address",

                value:
                    "GlowCare Industries",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "Common / Generic Name",

                value:
                    "Face Wash",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "Net Quantity",

                value:
                    "100 ml",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "MRP / Retail Sale Price",

                value:
                    "MRP ₹99",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "Consumer Care Details",

                value:
                    "Not detected",

                result:
                    "fail",

                resultText:
                    "✕ Failed"
            },

            {
                name:
                    "Importer / Packer Details",

                value:
                    "Not detected",

                result:
                    "fail",

                resultText:
                    "✕ Failed"
            }

        ],

        issue:
            "Consumer-care information and applicable packer/importer information could not be verified from the scanned label.",

        ruleReference:
            "The final compliance engine will attach the specific applicable Legal Metrology rule references to each failed declaration."

    },


    {
        id: "RPT-003",

        productName:
            "NutriChoice Almonds",

        manufacturer:
            "Healthy Foods India",

        quantity:
            "500 g",

        mrp:
            "₹420",

        country:
            "India",

        date:
            "10 Sep 2026",

        time:
            "11:05 AM",

        status:
            "review",

        statusText:
            "Needs Review",

        passed:
            10,

        total:
            12,

        checks: [

            {
                name:
                    "Manufacturer Name & Address",

                value:
                    "Healthy Foods India",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "Common / Generic Name",

                value:
                    "Almonds",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "Net Quantity",

                value:
                    "500 g",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "MRP / Retail Sale Price",

                value:
                    "MRP ₹420",

                result:
                    "pass",

                resultText:
                    "✓ Pass"
            },

            {
                name:
                    "Best Before / Use By",

                value:
                    "Text unclear",

                result:
                    "warning",

                resultText:
                    "⚠ Review"
            },

            {
                name:
                    "Consumer Care Details",

                value:
                    "Text partially detected",

                result:
                    "warning",

                resultText:
                    "⚠ Review"
            }

        ],

        issue:
            "Some label text could not be confidently extracted. Manual inspector verification is recommended.",

        ruleReference:
            "The compliance engine will identify the applicable requirements and flag low-confidence OCR results for manual review."

    }

];


/* =================================================
   ELEMENTS
================================================= */

const menuButton =
    document.getElementById(
        "menuButton"
    );

const sidebar =
    document.getElementById(
        "sidebar"
    );

const notificationButton =
    document.getElementById(
        "notificationButton"
    );

const reportsContainer =
    document.getElementById(
        "reportsContainer"
    );

const searchInput =
    document.getElementById(
        "searchInput"
    );

const statusFilter =
    document.getElementById(
        "statusFilter"
    );

const totalReports =
    document.getElementById(
        "totalReports"
    );

const compliantReports =
    document.getElementById(
        "compliantReports"
    );

const nonCompliantReports =
    document.getElementById(
        "nonCompliantReports"
    );

const reviewReports =
    document.getElementById(
        "reviewReports"
    );

const reportModal =
    document.getElementById(
        "reportModal"
    );

const modalClose =
    document.getElementById(
        "modalClose"
    );

const modalContent =
    document.getElementById(
        "modalContent"
    );

const generateButton =
    document.getElementById(
        "generateButton"
    );

const generateModal =
    document.getElementById(
        "generateModal"
    );

const generateClose =
    document.getElementById(
        "generateClose"
    );

const productSelect =
    document.getElementById(
        "productSelect"
    );

const modalGenerateButton =
    document.getElementById(
        "modalGenerateButton"
    );


/* =================================================
   MOBILE SIDEBAR
================================================= */

if (menuButton && sidebar) {

    menuButton.addEventListener(
        "click",
        function () {

            sidebar.classList.toggle(
                "open"
            );

        }
    );

}


document.addEventListener(
    "click",
    function (event) {

        if (window.innerWidth > 900) {
            return;
        }

        if (
            sidebar &&
            sidebar.classList.contains("open") &&
            !sidebar.contains(event.target) &&
            event.target !== menuButton
        ) {

            sidebar.classList.remove(
                "open"
            );

        }

    }
);


/* =================================================
   NOTIFICATIONS
================================================= */

if (notificationButton) {

    notificationButton.addEventListener(
        "click",
        function () {

            alert(
                "No new notifications."
            );

        }
    );

}


/* =================================================
   UPDATE STATISTICS
================================================= */

function updateStatistics() {

    const total =
        reportsData.length;


    const compliant =
        reportsData.filter(
            function (report) {

                return report.status ===
                    "compliant";

            }
        ).length;


    const nonCompliant =
        reportsData.filter(
            function (report) {

                return report.status ===
                    "non-compliant";

            }
        ).length;


    const review =
        reportsData.filter(
            function (report) {

                return report.status ===
                    "review";

            }
        ).length;


    totalReports.textContent =
        total;

    compliantReports.textContent =
        compliant;

    nonCompliantReports.textContent =
        nonCompliant;

    reviewReports.textContent =
        review;

}


/* =================================================
   DISPLAY REPORTS
================================================= */

function displayReports() {

    const searchTerm =
        searchInput.value
            .toLowerCase()
            .trim();


    const selectedStatus =
        statusFilter.value;


    const filteredReports =
        reportsData.filter(
            function (report) {

                const matchesSearch =
                    report.productName
                        .toLowerCase()
                        .includes(searchTerm) ||

                    report.manufacturer
                        .toLowerCase()
                        .includes(searchTerm);


                const matchesStatus =
                    selectedStatus === "all" ||
                    report.status === selectedStatus;


                return (
                    matchesSearch &&
                    matchesStatus
                );

            }
        );


    if (
        filteredReports.length === 0
    ) {

        reportsContainer.innerHTML = `

            <div class="empty-state">

                <div class="empty-state-icon">
                    ⌕
                </div>

                <h3>
                    No reports found
                </h3>

                <p>
                    Try changing your search or filter.
                </p>

            </div>

        `;

        return;

    }


    let tableHTML = `

        <table class="reports-table">

            <thead>

                <tr>

                    <th>
                        PRODUCT
                    </th>

                    <th>
                        REPORT ID
                    </th>

                    <th>
                        DATE
                    </th>

                    <th>
                        RESULT
                    </th>

                    <th>
                        CHECKS
                    </th>

                    <th>
                        ACTION
                    </th>

                </tr>

            </thead>

            <tbody>

    `;


    filteredReports.forEach(
        function (report) {

            tableHTML += `

                <tr>

                    <td>

                        <div class="product-cell">

                            <div class="product-image">
                                ▣
                            </div>

                            <div class="product-name">

                                <strong>
                                    ${report.productName}
                                </strong>

                                <span>
                                    ${report.manufacturer}
                                </span>

                            </div>

                        </div>

                    </td>


                    <td>
                        ${report.id}
                    </td>


                    <td>
                        ${report.date}
                    </td>


                    <td>

                        <span class="result-badge ${report.status}">

                            ${getStatusSymbol(report.status)}

                            ${report.statusText}

                        </span>

                    </td>


                    <td>

                        <span class="check-count">
                            ${report.passed}/${report.total} passed
                        </span>

                    </td>


                    <td>

                        <div class="action-buttons">

                            <button
                                class="view-button"
                                data-id="${report.id}">

                                View

                            </button>

                            <button
                                class="download-button"
                                data-id="${report.id}">

                                Export

                            </button>

                        </div>

                    </td>

                </tr>

            `;

        }
    );


    tableHTML += `

            </tbody>

        </table>

    `;


    reportsContainer.innerHTML =
        tableHTML;


    attachReportButtons();

}


/* =================================================
   STATUS SYMBOL
================================================= */

function getStatusSymbol(status) {

    if (status === "compliant") {
        return "✓";
    }

    if (status === "non-compliant") {
        return "✕";
    }

    return "⚠";

}


/* =================================================
   REPORT BUTTONS
================================================= */

function attachReportButtons() {

    const viewButtons =
        document.querySelectorAll(
            ".view-button"
        );


    const downloadButtons =
        document.querySelectorAll(
            ".download-button"
        );


    viewButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const reportId =
                        button.getAttribute(
                            "data-id"
                        );

                    openReport(
                        reportId
                    );

                }
            );

        }
    );


    downloadButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const reportId =
                        button.getAttribute(
                            "data-id"
                        );

                    exportReport(
                        reportId
                    );

                }
            );

        }
    );

}


/* =================================================
   OPEN REPORT
================================================= */

function openReport(reportId) {

    const report =
        reportsData.find(
            function (item) {

                return item.id === reportId;

            }
        );


    if (!report) {
        return;
    }


    let checksHTML = "";


    report.checks.forEach(
        function (check) {

            checksHTML += `

                <div class="compliance-row">

                    <strong>
                        ${check.name}
                    </strong>

                    <span>
                        ${check.value}
                    </span>

                    <span class="check-result ${check.result}">
                        ${check.resultText}
                    </span>

                </div>

            `;

        }
    );


    let issueHTML = "";


    if (report.issue) {

        issueHTML = `

            <div class="issue-box">

                <strong>
                    Compliance Observation
                </strong>

                <p>
                    ${report.issue}
                </p>

            </div>

        `;

    }


    modalContent.innerHTML = `

        <h2 class="modal-title">
            ${report.productName}
        </h2>

        <p class="modal-subtitle">
            ${report.id} • Generated ${report.date} at ${report.time}
        </p>


        <div class="report-overview">


            <div class="report-image-large">
                ▣
            </div>


            <div class="overview-info">


                <div class="info-box">

                    <span>
                        Manufacturer
                    </span>

                    <strong>
                        ${report.manufacturer}
                    </strong>

                </div>


                <div class="info-box">

                    <span>
                        Net Quantity
                    </span>

                    <strong>
                        ${report.quantity}
                    </strong>

                </div>


                <div class="info-box">

                    <span>
                        MRP
                    </span>

                    <strong>
                        ${report.mrp}
                    </strong>

                </div>


                <div class="info-box">

                    <span>
                        Country of Origin
                    </span>

                    <strong>
                        ${report.country}
                    </strong>

                </div>


                <div class="info-box">

                    <span>
                        Overall Result
                    </span>

                    <strong>
                        ${getStatusSymbol(report.status)}
                        ${report.statusText}
                    </strong>

                </div>


                <div class="info-box">

                    <span>
                        Verification Score
                    </span>

                    <strong>
                        ${report.passed}/${report.total} Checks Passed
                    </strong>

                </div>

            </div>

        </div>


        <h3 class="modal-section-title">
            Verification Details
        </h3>


        <div class="compliance-list">

            ${checksHTML}

        </div>


        ${issueHTML}


        <h3 class="modal-section-title">
            Rule / Verification Reference
        </h3>


        <div class="rule-reference">

            ${report.ruleReference}

        </div>

    `;


    reportModal.classList.add(
        "show"
    );

}


/* =================================================
   CLOSE REPORT MODAL
================================================= */

if (modalClose) {

    modalClose.addEventListener(
        "click",
        function () {

            reportModal.classList.remove(
                "show"
            );

        }
    );

}


/* Close when clicking outside */

if (reportModal) {

    reportModal.addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                reportModal
            ) {

                reportModal.classList.remove(
                    "show"
                );

            }

        }
    );

}


/* =================================================
   SEARCH
================================================= */

if (searchInput) {

    searchInput.addEventListener(
        "input",
        function () {

            displayReports();

        }
    );

}


/* =================================================
   FILTER
================================================= */

if (statusFilter) {

    statusFilter.addEventListener(
        "change",
        function () {

            displayReports();

        }
    );

}


/* =================================================
   GENERATE REPORT MODAL
================================================= */

if (generateButton) {

    generateButton.addEventListener(
        "click",
        function () {

            populateProductSelect();

            generateModal.classList.add(
                "show"
            );

        }
    );

}


/* =================================================
   POPULATE PRODUCT SELECT
================================================= */

function populateProductSelect() {

    productSelect.innerHTML = `

        <option value="">
            Select a product
        </option>

    `;


    reportsData.forEach(
        function (report) {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                report.id;


            option.textContent =
                report.productName;


            productSelect.appendChild(
                option
            );

        }
    );

}


/* =================================================
   CLOSE GENERATE MODAL
================================================= */

if (generateClose) {

    generateClose.addEventListener(
        "click",
        function () {

            generateModal.classList.remove(
                "show"
            );

        }
    );

}


/* =================================================
   GENERATE REPORT BUTTON
================================================= */

if (modalGenerateButton) {

    modalGenerateButton.addEventListener(
        "click",
        function () {

            const selectedId =
                productSelect.value;


            if (!selectedId) {

                alert(
                    "Please select a product first."
                );

                return;

            }


            generateModal.classList.remove(
                "show"
            );


            openReport(
                selectedId
            );

        }
    );

}


/* =================================================
   EXPORT REPORT
================================================= */

function exportReport(reportId) {

    const report =
        reportsData.find(
            function (item) {

                return item.id === reportId;

            }
        );


    if (!report) {
        return;
    }


    /*
        Temporary frontend export.

        Later this button can call the
        backend PDF/Excel generation API.
    */


    const reportText = `

METRISCAN
LEGAL METROLOGY COMPLIANCE REPORT

Report ID:
${report.id}

Product:
${report.productName}

Manufacturer:
${report.manufacturer}

Net Quantity:
${report.quantity}

MRP:
${report.mrp}

Country of Origin:
${report.country}

Date:
${report.date}

Time:
${report.time}

OVERALL RESULT:
${report.statusText}

VERIFICATION:
${report.passed}/${report.total} checks passed


VERIFICATION DETAILS

${report.checks.map(
    function (check) {

        return (
            check.name +
            " : " +
            check.value +
            " : " +
            check.resultText
        );

    }
).join("\n")}


OBSERVATION

${report.issue || "No compliance issues detected."}


RULE / VERIFICATION REFERENCE

${report.ruleReference}


Generated by METRISCAN
    `;


    const blob =
        new Blob(
            [reportText],
            {
                type:
                    "text/plain"
            }
        );


    const url =
        URL.createObjectURL(
            blob
        );


    const link =
        document.createElement(
            "a"
        );


    link.href = url;

    link.download =
        `${report.id}-METRISCAN-Report.txt`;


    document.body.appendChild(
        link
    );


    link.click();


    document.body.removeChild(
        link
    );


    URL.revokeObjectURL(
        url
    );

}


/* =================================================
   CLOSE MODALS WITH ESCAPE
================================================= */

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key !== "Escape") {
            return;
        }


        if (reportModal) {

            reportModal.classList.remove(
                "show"
            );

        }


        if (generateModal) {

            generateModal.classList.remove(
                "show"
            );

        }

    }
);


/* =================================================
   INITIALIZE
================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        updateStatistics();

        displayReports();

    }
);