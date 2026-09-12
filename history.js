/* =========================================
   METRISCAN - HISTORY JAVASCRIPT
========================================= */

const SETTINGS_KEY = "metriscanSettings";
const HISTORY_KEY = "metriscanHistory";


/* =========================================
   DEFAULT SETTINGS
========================================= */

const defaultSettings = {
    fullName: "Inspector Demo",
    role: "Inspector",
    email: "inspector@metriscan.in",
    organization: "METRISCAN Inspection Unit",
    theme: "dark",
    reportFormat: "PDF"
};


/* =========================================
   DEMO HISTORY DATA
========================================= */

const demoHistory = [

    {
        id: "MSC-001",
        product: "PureWash Detergent Powder",
        date: "2026-09-12",
        time: "10:42 AM",
        status: "compliant",
        checksPassed: 12,
        totalChecks: 12
    },

    {
        id: "MSC-002",
        product: "FreshGlow Face Wash",
        date: "2026-09-11",
        time: "04:18 PM",
        status: "non-compliant",
        checksPassed: 9,
        totalChecks: 12
    },

    {
        id: "MSC-003",
        product: "NutriChoice Almonds",
        date: "2026-09-10",
        time: "02:35 PM",
        status: "review",
        checksPassed: 10,
        totalChecks: 12
    },

    {
        id: "MSC-004",
        product: "CleanHome Floor Cleaner",
        date: "2026-09-09",
        time: "11:20 AM",
        status: "compliant",
        checksPassed: 12,
        totalChecks: 12
    },

    {
        id: "MSC-005",
        product: "GlowCare Shampoo",
        date: "2026-09-07",
        time: "05:45 PM",
        status: "compliant",
        checksPassed: 11,
        totalChecks: 12
    },

    {
        id: "MSC-006",
        product: "DailyFresh Cooking Oil",
        date: "2026-09-05",
        time: "01:15 PM",
        status: "non-compliant",
        checksPassed: 8,
        totalChecks: 12
    },

    {
        id: "MSC-007",
        product: "SoftTouch Hand Wash",
        date: "2026-08-29",
        time: "03:22 PM",
        status: "review",
        checksPassed: 10,
        totalChecks: 12
    },

    {
        id: "MSC-008",
        product: "NatureBest Green Tea",
        date: "2026-08-20",
        time: "12:40 PM",
        status: "compliant",
        checksPassed: 12,
        totalChecks: 12
    }

];


/* =========================================
   GET SETTINGS
========================================= */

function getSettings() {

    const savedSettings =
        JSON.parse(
            localStorage.getItem(SETTINGS_KEY)
        ) || {};

    return {
        ...defaultSettings,
        ...savedSettings
    };
}


/* =========================================
   THEME
========================================= */

function applySavedTheme() {

    const settings = getSettings();

    if (settings.theme === "light") {

        document.body.classList.add("light-theme");

    } else {

        document.body.classList.remove("light-theme");

    }
}


/* =========================================
   LOAD USER PROFILE
========================================= */

function loadUserProfile() {

    const settings = getSettings();

    const name =
        settings.fullName || "Inspector Demo";

    const role =
        settings.role || "Inspector";


    const nameElement =
        document.getElementById("historyUserName");

    const roleElement =
        document.getElementById("historyUserRole");

    const avatarElement =
        document.getElementById("historyAvatar");


    if (nameElement) {
        nameElement.textContent = name;
    }

    if (roleElement) {
        roleElement.textContent = role;
    }


    /* Generate initials */

    if (avatarElement) {

        const words =
            name
                .trim()
                .split(/\s+/)
                .filter(Boolean);

        let initials = "ID";

        if (words.length === 1) {

            initials =
                words[0]
                    .substring(0, 2)
                    .toUpperCase();

        } else if (words.length > 1) {

            initials =
                (
                    words[0][0] +
                    words[words.length - 1][0]
                ).toUpperCase();
        }

        avatarElement.textContent = initials;
    }
}


/* =========================================
   GET HISTORY
========================================= */

function getHistory() {

    const savedHistory =
        JSON.parse(
            localStorage.getItem(HISTORY_KEY)
        );

    /*
       For now use demo data.

       Once backend/scan page is connected,
       scan results can be pushed into
       metriscanHistory.
    */

    if (
        Array.isArray(savedHistory) &&
        savedHistory.length > 0
    ) {

        return savedHistory;

    }

    return demoHistory;
}


/* =========================================
   SAVE HISTORY
========================================= */

function saveHistory(history) {

    localStorage.setItem(
        HISTORY_KEY,
        JSON.stringify(history)
    );
}


/* =========================================
   UPDATE STATISTICS
========================================= */

function updateStatistics(history) {

    const total =
        history.length;

    const compliant =
        history.filter(
            item => item.status === "compliant"
        ).length;

    const nonCompliant =
        history.filter(
            item => item.status === "non-compliant"
        ).length;

    const review =
        history.filter(
            item => item.status === "review"
        ).length;


    document.getElementById("totalScans").textContent =
        total;

    document.getElementById("compliantScans").textContent =
        compliant;

    document.getElementById("nonCompliantScans").textContent =
        nonCompliant;

    document.getElementById("reviewScans").textContent =
        review;
}


/* =========================================
   STATUS TEXT
========================================= */

function getStatusText(status) {

    if (status === "compliant") {
        return "Compliant";
    }

    if (status === "non-compliant") {
        return "Non-Compliant";
    }

    if (status === "review") {
        return "Needs Review";
    }

    return "Unknown";
}


/* =========================================
   RENDER TABLE
========================================= */

function renderHistory(history) {

    const tableBody =
        document.getElementById(
            "historyTableBody"
        );

    const emptyState =
        document.getElementById(
            "emptyState"
        );

    const resultCount =
        document.getElementById(
            "resultCount"
        );


    tableBody.innerHTML = "";


    resultCount.textContent =
        `${history.length} ${
            history.length === 1
                ? "scan"
                : "scans"
        }`;


    if (history.length === 0) {

        emptyState.style.display = "block";

        document.querySelector(
            ".history-table"
        ).style.display = "none";

        return;
    }


    emptyState.style.display = "none";

    document.querySelector(
        ".history-table"
    ).style.display = "table";


    history.forEach(function (item, index) {

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>
                <span class="scan-id">
                    ${item.id}
                </span>
            </td>


            <td>

                <div class="product-cell">

                    <div class="product-icon">
                        <i class="fas fa-box"></i>
                    </div>

                    <span class="product-name">
                        ${item.product}
                    </span>

                </div>

            </td>


            <td>

                <div class="date-cell">

                    <span class="date-main">
                        ${formatDate(item.date)}
                    </span>

                    <span class="date-time">
                        ${item.time}
                    </span>

                </div>

            </td>


            <td>

                <span class="status-badge ${item.status}">

                    <i class="${getStatusIcon(item.status)}"></i>

                    ${getStatusText(item.status)}

                </span>

            </td>


            <td>

                <span class="check-count">

                    <strong>
                        ${item.checksPassed}
                    </strong>

                    / ${item.totalChecks}

                </span>

            </td>


            <td>

                <button
                    class="view-btn"
                    data-index="${index}"
                >

                    <i class="fas fa-eye"></i>

                    View

                </button>

            </td>

        `;


        tableBody.appendChild(row);

    });


    setupViewButtons();
}


/* =========================================
   STATUS ICON
========================================= */

function getStatusIcon(status) {

    if (status === "compliant") {
        return "fas fa-circle-check";
    }

    if (status === "non-compliant") {
        return "fas fa-circle-xmark";
    }

    return "fas fa-triangle-exclamation";
}


/* =========================================
   FORMAT DATE
========================================= */

function formatDate(dateString) {

    const date =
        new Date(dateString + "T00:00:00");

    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );
}


/* =========================================
   FILTER HISTORY
========================================= */

function filterHistory() {

    const searchValue =
        document
            .getElementById("searchInput")
            .value
            .toLowerCase()
            .trim();


    const statusValue =
        document.getElementById(
            "statusFilter"
        ).value;


    const dateValue =
        document.getElementById(
            "dateFilter"
        ).value;


    const history =
        getHistory();


    const today =
        new Date();


    const filtered =
        history.filter(function (item) {

            /* SEARCH */

            const matchesSearch =
                item.product
                    .toLowerCase()
                    .includes(searchValue)
                ||
                item.id
                    .toLowerCase()
                    .includes(searchValue);


            /* STATUS */

            const matchesStatus =
                statusValue === "all"
                ||
                item.status === statusValue;


            /* DATE */

            let matchesDate = true;

            const itemDate =
                new Date(
                    item.date + "T00:00:00"
                );


            if (dateValue === "today") {

                matchesDate =
                    itemDate.toDateString() ===
                    today.toDateString();

            }


            if (dateValue === "week") {

                const sevenDaysAgo =
                    new Date();

                sevenDaysAgo.setDate(
                    today.getDate() - 7
                );

                matchesDate =
                    itemDate >= sevenDaysAgo;

            }


            if (dateValue === "month") {

                const thirtyDaysAgo =
                    new Date();

                thirtyDaysAgo.setDate(
                    today.getDate() - 30
                );

                matchesDate =
                    itemDate >= thirtyDaysAgo;

            }


            return (
                matchesSearch &&
                matchesStatus &&
                matchesDate
            );

        });


    renderHistory(filtered);
}


/* =========================================
   VIEW DETAILS
========================================= */

function openDetails(index) {

    const history =
        getHistory();

    const item =
        history[index];

    if (!item) return;


    document.getElementById(
        "modalProductName"
    ).textContent =
        item.product;


    document.getElementById(
        "modalScanId"
    ).textContent =
        item.id;


    document.getElementById(
        "modalDate"
    ).textContent =
        formatDate(item.date);


    document.getElementById(
        "modalTime"
    ).textContent =
        item.time;


    document.getElementById(
        "modalStatus"
    ).textContent =
        getStatusText(item.status);


    document.getElementById(
        "modalChecks"
    ).textContent =
        `${item.checksPassed} / ${item.totalChecks}`;


    document.getElementById(
        "detailsModal"
    ).classList.add("show");
}


/* =========================================
   CLOSE MODAL
========================================= */

function closeDetails() {

    document.getElementById(
        "detailsModal"
    ).classList.remove("show");
}


/* =========================================
   VIEW BUTTONS
========================================= */

function setupViewButtons() {

    const buttons =
        document.querySelectorAll(
            ".view-btn"
        );


    buttons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                const index =
                    Number(
                        this.dataset.index
                    );

                openDetails(index);

            }
        );

    });
}


/* =========================================
   RESET FILTERS
========================================= */

function resetFilters() {

    document.getElementById(
        "searchInput"
    ).value = "";


    document.getElementById(
        "statusFilter"
    ).value = "all";


    document.getElementById(
        "dateFilter"
    ).value = "all";


    renderHistory(
        getHistory()
    );
}


/* =========================================
   CLEAR HISTORY
========================================= */

function clearHistory() {

    const confirmed =
        confirm(
            "Are you sure you want to clear your complete scan history?"
        );


    if (!confirmed) {
        return;
    }


    localStorage.removeItem(
        HISTORY_KEY
    );


    renderHistory([]);

    updateStatistics([]);
}


/* =========================================
   MOBILE SIDEBAR
========================================= */

function setupMobileSidebar() {

    const menuBtn =
        document.getElementById(
            "menuBtn"
        );

    const sidebar =
        document.querySelector(
            ".sidebar"
        );


    if (!menuBtn || !sidebar) {
        return;
    }


    menuBtn.addEventListener(
        "click",
        function () {

            sidebar.classList.toggle(
                "open"
            );

        }
    );
}


/* =========================================
   MODAL OUTSIDE CLICK
========================================= */

function setupModalOutsideClick() {

    const modal =
        document.getElementById(
            "detailsModal"
        );


    modal.addEventListener(
        "click",
        function (event) {

            if (event.target === modal) {

                closeDetails();

            }

        }
    );
}


/* =========================================
   ESCAPE KEY
========================================= */

function setupEscapeKey() {

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeDetails();

            }

        }
    );
}


/* =========================================
   INITIALIZE
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        applySavedTheme();

        loadUserProfile();

        const history =
            getHistory();

        updateStatistics(history);

        renderHistory(history);

        setupMobileSidebar();

        setupModalOutsideClick();

        setupEscapeKey();


        /* SEARCH */

        document
            .getElementById("searchInput")
            .addEventListener(
                "input",
                filterHistory
            );


        /* STATUS FILTER */

        document
            .getElementById("statusFilter")
            .addEventListener(
                "change",
                filterHistory
            );


        /* DATE FILTER */

        document
            .getElementById("dateFilter")
            .addEventListener(
                "change",
                filterHistory
            );


        /* RESET */

        document
            .getElementById("resetFilters")
            .addEventListener(
                "click",
                resetFilters
            );


        /* CLEAR HISTORY */

        document
            .getElementById("clearHistoryBtn")
            .addEventListener(
                "click",
                clearHistory
            );


        /* CLOSE MODAL */

        document
            .getElementById("closeModal")
            .addEventListener(
                "click",
                closeDetails
            );


        document
            .getElementById("modalCloseBtn")
            .addEventListener(
                "click",
                closeDetails
            );

    }
);