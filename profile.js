// =========================
// METRISCAN PROFILE
// =========================

const SETTINGS_KEY = "metriscanSettings";


// =========================
// DEFAULT SETTINGS
// =========================

const defaultSettings = {
    fullName: "Inspector Demo",
    role: "Inspector",
    email: "inspector@metriscan.in",
    organization: "METRISCAN Inspection Unit",
    theme: "dark",
    reportFormat: "PDF"
};


// =========================
// GET SAVED SETTINGS
// =========================

function getSettings() {

    const savedSettings =
        JSON.parse(localStorage.getItem(SETTINGS_KEY)) || {};

    return {
        ...defaultSettings,
        ...savedSettings
    };
}


// =========================
// APPLY GLOBAL THEME
// =========================

function applySavedTheme() {

    const settings = getSettings();

    if (settings.theme === "light") {

        document.body.classList.add("light-theme");

    } else {

        document.body.classList.remove("light-theme");

    }
}


// =========================
// LOAD PROFILE DATA
// =========================

function loadProfile() {

    const settings = getSettings();

    const fullNameInput =
        document.getElementById("fullName");

    const roleInput =
        document.getElementById("role");

    const emailInput =
        document.getElementById("email");

    const organizationInput =
        document.getElementById("organization");


    if (fullNameInput) {
        fullNameInput.value = settings.fullName;
    }

    if (roleInput) {
        roleInput.value = settings.role;
    }

    if (emailInput) {
        emailInput.value = settings.email;
    }

    if (organizationInput) {
        organizationInput.value = settings.organization;
    }


    updateProfileDisplay(settings);

    updatePreferences(settings);
}


// =========================
// UPDATE PROFILE DISPLAY
// =========================

function updateProfileDisplay(settings) {

    const name =
        settings.fullName || "Inspector Demo";

    const organization =
        settings.organization ||
        "METRISCAN Inspection Unit";


    const heroName =
        document.getElementById("heroName");

    const heroOrganization =
        document.getElementById("heroOrganization");

    const topName =
        document.getElementById("topName");

    const avatarCircle =
        document.getElementById("avatarCircle");


    if (heroName) {
        heroName.textContent = name;
    }

    if (heroOrganization) {
        heroOrganization.textContent = organization;
    }

    if (topName) {
        topName.textContent = name;
    }


    // Generate initials for avatar

    if (avatarCircle) {

        const words =
            name.trim().split(/\s+/).filter(Boolean);

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


        avatarCircle.textContent = initials;
    }
}


// =========================
// UPDATE PREFERENCES
// =========================

function updatePreferences(settings) {

    const themeValue =
        document.getElementById("themeValue");

    const reportFormatValue =
        document.getElementById("reportFormatValue");


    if (themeValue) {

        themeValue.textContent =
            settings.theme === "light"
                ? "Light"
                : "Dark";
    }


    if (reportFormatValue) {

        reportFormatValue.textContent =
            settings.reportFormat || "PDF";
    }
}


// =========================
// SAVE PROFILE
// =========================

function saveProfile() {

    const settings = getSettings();


    const fullNameInput =
        document.getElementById("fullName");

    const roleInput =
        document.getElementById("role");

    const emailInput =
        document.getElementById("email");

    const organizationInput =
        document.getElementById("organization");


    settings.fullName =
        fullNameInput?.value.trim() ||
        "Inspector Demo";

    settings.role =
        roleInput?.value.trim() ||
        "Inspector";

    settings.email =
        emailInput?.value.trim() ||
        "inspector@metriscan.in";

    settings.organization =
        organizationInput?.value.trim() ||
        "METRISCAN Inspection Unit";


    // Save without deleting theme or other settings

    localStorage.setItem(
        SETTINGS_KEY,
        JSON.stringify(settings)
    );


    updateProfileDisplay(settings);

    updatePreferences(settings);


    showSaveMessage(
        "✓ Profile saved successfully"
    );
}


// =========================
// SAVE MESSAGE
// =========================

function showSaveMessage(message) {

    const saveMessage =
        document.getElementById("saveMessage");

    if (!saveMessage) {
        return;
    }

    saveMessage.textContent = message;


    setTimeout(function () {

        saveMessage.textContent = "";

    }, 3000);
}


// =========================
// OPEN EDIT PROFILE MODAL
// =========================

function openProfileModal() {

    const settings = getSettings();


    const modal =
        document.getElementById("profileModal");

    const modalName =
        document.getElementById("modalName");

    const modalOrganization =
        document.getElementById("modalOrganization");


    if (modalName) {
        modalName.value = settings.fullName;
    }

    if (modalOrganization) {
        modalOrganization.value =
            settings.organization;
    }


    if (modal) {
        modal.classList.add("show");
    }
}


// =========================
// CLOSE EDIT PROFILE MODAL
// =========================

function closeProfileModal() {

    const modal =
        document.getElementById("profileModal");

    if (modal) {
        modal.classList.remove("show");
    }
}


// =========================
// SAVE MODAL PROFILE
// =========================

function saveModalProfile() {

    const settings = getSettings();


    const modalName =
        document.getElementById("modalName");

    const modalOrganization =
        document.getElementById("modalOrganization");


    settings.fullName =
        modalName?.value.trim() ||
        "Inspector Demo";

    settings.organization =
        modalOrganization?.value.trim() ||
        "METRISCAN Inspection Unit";


    localStorage.setItem(
        SETTINGS_KEY,
        JSON.stringify(settings)
    );


    loadProfile();

    closeProfileModal();


    showSaveMessage(
        "✓ Profile updated successfully"
    );
}


// =========================
// CHANGE PASSWORD
// =========================

function handleChangePassword() {

    alert(
        "Password management will be connected to the backend authentication system."
    );
}


// =========================
// TWO-FACTOR AUTHENTICATION
// =========================

function handleTwoFactorChange(event) {

    if (event.target.checked) {

        alert(
            "Two-Factor Authentication will be connected to the authentication backend."
        );

    }

}


// =========================
// MOBILE SIDEBAR
// =========================

function setupMobileSidebar() {

    const menuBtn =
        document.getElementById("menuBtn");

    const sidebar =
        document.querySelector(".sidebar");


    if (!menuBtn || !sidebar) {
        return;
    }


    menuBtn.addEventListener(
        "click",
        function () {

            sidebar.classList.toggle("open");

        }
    );
}


// =========================
// MODAL OUTSIDE CLICK
// =========================

function setupModalOutsideClick() {

    const modal =
        document.getElementById("profileModal");


    if (!modal) {
        return;
    }


    modal.addEventListener(
        "click",
        function (event) {

            if (event.target === modal) {

                closeProfileModal();

            }

        }
    );
}


// =========================
// ESC KEY
// =========================

function setupEscapeKey() {

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeProfileModal();

            }

        }
    );
}


// =========================
// INITIALIZE
// =========================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        // Apply global theme FIRST
        applySavedTheme();

        // Load saved profile
        loadProfile();

        // Mobile sidebar
        setupMobileSidebar();

        // Edit profile
        const editProfileBtn =
            document.getElementById("editProfileBtn");

        if (editProfileBtn) {

            editProfileBtn.addEventListener(
                "click",
                openProfileModal
            );

        }


        // Save profile
        const saveProfileBtn =
            document.getElementById("saveProfile");

        if (saveProfileBtn) {

            saveProfileBtn.addEventListener(
                "click",
                saveProfile
            );

        }


        // Close modal
        const closeModalBtn =
            document.getElementById("closeModal");

        if (closeModalBtn) {

            closeModalBtn.addEventListener(
                "click",
                closeProfileModal
            );

        }


        // Cancel modal
        const cancelModalBtn =
            document.getElementById("cancelModal");

        if (cancelModalBtn) {

            cancelModalBtn.addEventListener(
                "click",
                closeProfileModal
            );

        }


        // Save modal
        const modalSaveBtn =
            document.getElementById("modalSave");

        if (modalSaveBtn) {

            modalSaveBtn.addEventListener(
                "click",
                saveModalProfile
            );

        }


        // Change password
        const changePasswordBtn =
            document.getElementById("changePassword");

        if (changePasswordBtn) {

            changePasswordBtn.addEventListener(
                "click",
                handleChangePassword
            );

        }


        // Two-factor authentication
        const twoFactorToggle =
            document.getElementById("twoFactor");

        if (twoFactorToggle) {

            twoFactorToggle.addEventListener(
                "change",
                handleTwoFactorChange
            );

        }


        // Modal outside click
        setupModalOutsideClick();

        // ESC key
        setupEscapeKey();

    }
);