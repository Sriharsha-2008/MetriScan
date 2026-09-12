/* =========================================
   METRISCAN SETTINGS
   setting.js
========================================= */


/* =========================
   ELEMENTS
========================= */

const menuButton =
    document.getElementById("menuButton");

const sidebar =
    document.getElementById("sidebar");

const notificationButton =
    document.getElementById("notificationButton");

const settingsMenuItems =
    document.querySelectorAll(
        ".settings-menu-item"
    );

const settingsPanels =
    document.querySelectorAll(
        ".settings-panel"
    );

const saveButton =
    document.getElementById("saveButton");

const resetButton =
    document.getElementById("resetButton");

const saveMessage =
    document.getElementById("saveMessage");

const themeSelect =
    document.getElementById("theme");


/* =========================
   DEFAULT SETTINGS
========================= */

const defaultSettings = {

    fullName:
        "Inspector Demo",

    role:
        "Inspector",

    email:
        "inspector@metriscan.com",

    organization:
        "Legal Metrology Department",

    scanNotification:
        true,

    complianceNotification:
        true,

    reportNotification:
        true,

    autoVerification:
        true,

    manualReview:
        false,

    saveHistory:
        true,

    autoSaveReports:
        true,

    ruleReferences:
        true,

    reportFormat:
        "pdf",

    theme:
        "dark",

    language:
        "english",

    compactMode:
        false

};


/* =========================
   MOBILE SIDEBAR
========================= */

if (menuButton && sidebar) {

    menuButton.addEventListener(
        "click",
        function () {

            sidebar.classList.toggle("open");

        }
    );

}


/* Close sidebar outside click */

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

            sidebar.classList.remove("open");

        }

    }
);


/* =========================
   NOTIFICATION
========================= */

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


/* =========================
   SETTINGS NAVIGATION
========================= */

settingsMenuItems.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                const targetSection =
                    button.getAttribute(
                        "data-section"
                    );


                /* Remove active from all buttons */

                settingsMenuItems.forEach(
                    function (item) {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


                /* Activate clicked button */

                button.classList.add(
                    "active"
                );


                /* Hide all panels */

                settingsPanels.forEach(
                    function (panel) {

                        panel.classList.remove(
                            "active"
                        );

                    }
                );


                /* Show selected panel */

                const targetPanel =
                    document.getElementById(
                        targetSection
                    );


                if (targetPanel) {

                    targetPanel.classList.add(
                        "active"
                    );

                }

            }
        );

    }
);


/* =========================
   THEME
========================= */

function applyTheme(theme) {

    if (theme === "light") {

        document.body.classList.add(
            "light-theme"
        );

    } else {

        document.body.classList.remove(
            "light-theme"
        );

    }

}


/* =========================
   THEME SELECT CHANGE
========================= */

if (themeSelect) {

    themeSelect.addEventListener(
        "change",
        function () {

            applyTheme(
                this.value
            );

        }
    );

}


/* =========================
   HELPER: SET VALUE
========================= */

function setValue(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );


    if (
        element &&
        value !== undefined
    ) {

        element.value = value;

    }

}


/* =========================
   HELPER: SET CHECKBOX
========================= */

function setChecked(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );


    if (
        element &&
        value !== undefined
    ) {

        element.checked =
            Boolean(value);

    }

}


/* =========================
   APPLY SETTINGS
========================= */

function applySettings(settings) {

    /* Apply theme first */

    applyTheme(
        settings.theme || "dark"
    );


    /* Account */

    setValue(
        "fullName",
        settings.fullName
    );

    setValue(
        "role",
        settings.role
    );

    setValue(
        "email",
        settings.email
    );

    setValue(
        "organization",
        settings.organization
    );


    /* Notifications */

    setChecked(
        "scanNotification",
        settings.scanNotification
    );

    setChecked(
        "complianceNotification",
        settings.complianceNotification
    );

    setChecked(
        "reportNotification",
        settings.reportNotification
    );


    /* Scanner */

    setChecked(
        "autoVerification",
        settings.autoVerification
    );

    setChecked(
        "manualReview",
        settings.manualReview
    );

    setChecked(
        "saveHistory",
        settings.saveHistory
    );


    /* Reports */

    setChecked(
        "autoSaveReports",
        settings.autoSaveReports
    );

    setChecked(
        "ruleReferences",
        settings.ruleReferences
    );

    setValue(
        "reportFormat",
        settings.reportFormat
    );


    /* Appearance */

    setValue(
        "theme",
        settings.theme || "dark"
    );

    setValue(
        "language",
        settings.language
    );

    setChecked(
        "compactMode",
        settings.compactMode
    );

}


/* =========================
   GET CURRENT SETTINGS
========================= */

function getCurrentSettings() {

    return {

        /* Account */

        fullName:
            document.getElementById(
                "fullName"
            ).value,

        role:
            document.getElementById(
                "role"
            ).value,

        email:
            document.getElementById(
                "email"
            ).value,

        organization:
            document.getElementById(
                "organization"
            ).value,


        /* Notifications */

        scanNotification:
            document.getElementById(
                "scanNotification"
            ).checked,

        complianceNotification:
            document.getElementById(
                "complianceNotification"
            ).checked,

        reportNotification:
            document.getElementById(
                "reportNotification"
            ).checked,


        /* Scanner */

        autoVerification:
            document.getElementById(
                "autoVerification"
            ).checked,

        manualReview:
            document.getElementById(
                "manualReview"
            ).checked,

        saveHistory:
            document.getElementById(
                "saveHistory"
            ).checked,


        /* Reports */

        autoSaveReports:
            document.getElementById(
                "autoSaveReports"
            ).checked,

        ruleReferences:
            document.getElementById(
                "ruleReferences"
            ).checked,

        reportFormat:
            document.getElementById(
                "reportFormat"
            ).value,


        /* Appearance */

        theme:
            document.getElementById(
                "theme"
            ).value,

        language:
            document.getElementById(
                "language"
            ).value,

        compactMode:
            document.getElementById(
                "compactMode"
            ).checked

    };

}


/* =========================
   SAVE SETTINGS
========================= */

if (saveButton) {

    saveButton.addEventListener(
        "click",
        function () {

            const settings =
                getCurrentSettings();


            localStorage.setItem(
                "metriscanSettings",
                JSON.stringify(settings)
            );


            showSaveMessage();

        }
    );

}


/* =========================
   SAVE MESSAGE
========================= */

function showSaveMessage() {

    if (!saveMessage) {
        return;
    }


    saveMessage.classList.add(
        "show"
    );


    setTimeout(
        function () {

            saveMessage.classList.remove(
                "show"
            );

        },
        3000
    );

}


/* =========================
   RESET SETTINGS
========================= */

if (resetButton) {

    resetButton.addEventListener(
        "click",
        function () {

            const confirmed =
                confirm(
                    "Are you sure you want to reset all settings to their default values?"
                );


            if (!confirmed) {
                return;
            }


            localStorage.removeItem(
                "metriscanSettings"
            );


            applySettings(
                defaultSettings
            );


            showSaveMessage();

        }
    );

}


/* =========================
   LOAD SAVED SETTINGS
========================= */

function loadSettings() {

    const savedSettings =
        localStorage.getItem(
            "metriscanSettings"
        );


    if (!savedSettings) {

        applySettings(
            defaultSettings
        );

        return;

    }


    try {

        const settings =
            JSON.parse(
                savedSettings
            );


        applySettings(
            settings
        );

    }

    catch (error) {

        console.error(
            "Could not load METRISCAN settings:",
            error
        );


        applySettings(
            defaultSettings
        );

    }

}


/* =========================
   INITIALIZE
========================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadSettings();

    }
);