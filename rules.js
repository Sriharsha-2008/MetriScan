/* =========================================
   METRISCAN - METROLOGY RULES JAVASCRIPT
========================================= */

const SETTINGS_KEY = "metriscanSettings";


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
   METROLOGY RULES
========================================= */

const metrologyRules = [

    {
        number: 1,

        declaration:
            "Manufacturer Name & Address",

        applicability:
            "Mandatory",

        category:
            "mandatory",

        scannerCheck:
            "Manufacturer name and complete address are present"
    },


    {
        number: 2,

        declaration:
            "Packer Name & Address",

        applicability:
            "Where applicable",

        category:
            "applicable",

        scannerCheck:
            "Packer details are present"
    },


    {
        number: 3,

        declaration:
            "Importer Name & Address",

        applicability:
            "Imported products",

        category:
            "imported",

        scannerCheck:
            "Importer details are present"
    },


    {
        number: 4,

        declaration:
            "Common / Generic Name",

        applicability:
            "Mandatory",

        category:
            "mandatory",

        scannerCheck:
            "Common/generic name of the commodity is declared"
    },


    {
        number: 5,

        declaration:
            "Net Quantity",

        applicability:
            "Mandatory",

        category:
            "mandatory",

        scannerCheck:
            "Quantity and appropriate unit are declared"
    },


    {
        number: 6,

        declaration:
            "MRP / Retail Sale Price",

        applicability:
            "Mandatory",

        category:
            "mandatory",

        scannerCheck:
            "MRP is present and expressed appropriately"
    },


    {
        number: 7,

        declaration:
            "Unit Sale Price",

        applicability:
            "Applicable packages",

        category:
            "applicable",

        scannerCheck:
            "Unit sale price is declared with appropriate unit"
    },


    {
        number: 8,

        declaration:
            "Manufacturing / Pre-packing / Import Date",

        applicability:
            "Commodity-dependent",

        category:
            "commodity",

        scannerCheck:
            "Applicable month/year declaration is present and valid"
    },


    {
        number: 9,

        declaration:
            "Best Before / Use By",

        applicability:
            "Conditional",

        category:
            "conditional",

        scannerCheck:
            "Present where the commodity can become unfit for consumption"
    },


    {
        number: 10,

        declaration:
            "Consumer Care Details",

        applicability:
            "Mandatory",

        category:
            "mandatory",

        scannerCheck:
            "Consumer-care contact information is present"
    },


    {
        number: 11,

        declaration:
            "Country of Origin",

        applicability:
            "Imported products",

        category:
            "imported",

        scannerCheck:
            "Country of origin is declared"
    },


    {
        number: 12,

        declaration:
            "Dimensions",

        applicability:
            "Where applicable",

        category:
            "applicable",

        scannerCheck:
            "Dimensions are declared for commodities where size is relevant"
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
   APPLY THEME
========================================= */

function applySavedTheme() {

    const settings = getSettings();

    if (settings.theme === "light") {

        document.body.classList.add(
            "light-theme"
        );

    } else {

        document.body.classList.remove(
            "light-theme"
        );

    }
}


/* =========================================
   LOAD PROFILE
========================================= */

function loadUserProfile() {

    const settings = getSettings();

    const name =
        settings.fullName ||
        "Inspector Demo";

    const role =
        settings.role ||
        "Inspector";


    const nameElement =
        document.getElementById(
            "rulesUserName"
        );

    const roleElement =
        document.getElementById(
            "rulesUserRole"
        );

    const avatarElement =
        document.getElementById(
            "rulesAvatar"
        );


    if (nameElement) {

        nameElement.textContent =
            name;

    }


    if (roleElement) {

        roleElement.textContent =
            role;

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

        }

        else if (words.length > 1) {

            initials =
                (
                    words[0][0] +
                    words[words.length - 1][0]
                ).toUpperCase();

        }


        avatarElement.textContent =
            initials;
    }
}


/* =========================================
   GET CATEGORY CLASS
========================================= */

function getApplicabilityClass(category) {

    if (category === "mandatory") {

        return "mandatory";

    }

    if (category === "imported") {

        return "imported";

    }

    if (category === "conditional") {

        return "conditional";

    }

    return "";
}


/* =========================================
   RENDER RULES
========================================= */

function renderRules(rules) {

    const tableBody =
        document.getElementById(
            "rulesTableBody"
        );

    const emptyState =
        document.getElementById(
            "emptyState"
        );

    const visibleCount =
        document.getElementById(
            "visibleCount"
        );


    tableBody.innerHTML = "";


    visibleCount.textContent =
        `${rules.length} ${
            rules.length === 1
                ? "Rule"
                : "Rules"
        }`;


    if (rules.length === 0) {

        document.querySelector(
            ".rules-table"
        ).style.display = "none";

        emptyState.style.display =
            "block";

        return;
    }


    document.querySelector(
        ".rules-table"
    ).style.display = "table";

    emptyState.style.display =
        "none";


    rules.forEach(function (rule) {

        const row =
            document.createElement("tr");


        row.innerHTML = `

            <td>

                <span class="rule-number">
                    ${rule.number}
                </span>

            </td>


            <td>

                <div class="declaration">
                    ${rule.declaration}
                </div>

            </td>


            <td>

                <div class="applicability">

                    <span
                        class="applicability-badge ${getApplicabilityClass(rule.category)}"
                    >
                        ${rule.applicability}
                    </span>

                </div>

            </td>


            <td>

                <div class="scanner-check">
                    ${rule.scannerCheck}
                </div>

            </td>

        `;


        tableBody.appendChild(row);

    });
}


/* =========================================
   FILTER RULES
========================================= */

function filterRules() {

    const searchInput =
        document.getElementById(
            "ruleSearch"
        );

    const applicabilityFilter =
        document.getElementById(
            "applicabilityFilter"
        );


    const searchValue =
        searchInput.value
            .toLowerCase()
            .trim();


    const filterValue =
        applicabilityFilter.value;


    const filteredRules =
        metrologyRules.filter(
            function (rule) {


                /* SEARCH */

                const matchesSearch =

                    rule.declaration
                        .toLowerCase()
                        .includes(searchValue)

                    ||

                    rule.applicability
                        .toLowerCase()
                        .includes(searchValue)

                    ||

                    rule.scannerCheck
                        .toLowerCase()
                        .includes(searchValue);


                /* FILTER */

                const matchesFilter =

                    filterValue === "all"

                    ||

                    rule.category ===
                    filterValue;


                return (
                    matchesSearch &&
                    matchesFilter
                );

            }
        );


    renderRules(
        filteredRules
    );
}


/* =========================================
   RESET
========================================= */

function resetRules() {

    document.getElementById(
        "ruleSearch"
    ).value = "";


    document.getElementById(
        "applicabilityFilter"
    ).value = "all";


    renderRules(
        metrologyRules
    );
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
   INITIALIZE
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        applySavedTheme();

        loadUserProfile();

        renderRules(
            metrologyRules
        );

        setupMobileSidebar();


        /* SEARCH */

        document
            .getElementById(
                "ruleSearch"
            )
            .addEventListener(
                "input",
                filterRules
            );


        /* FILTER */

        document
            .getElementById(
                "applicabilityFilter"
            )
            .addEventListener(
                "change",
                filterRules
            );


        /* RESET */

        document
            .getElementById(
                "resetRules"
            )
            .addEventListener(
                "click",
                resetRules
            );

    }
);