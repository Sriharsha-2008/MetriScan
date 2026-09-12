/* =========================
   SIDEBAR TOGGLE
========================= */

const menuBtn = document.getElementById("menuBtn");

const sidebar = document.querySelector(".sidebar");

menuBtn.addEventListener("click", function () {

    sidebar.classList.toggle("open");

});


/* =========================
   FILE UPLOAD
========================= */

const chooseBtn = document.getElementById("chooseBtn");

const fileInput = document.getElementById("fileInput");

const uploadArea = document.getElementById("uploadArea");


chooseBtn.addEventListener("click", function () {

    fileInput.click();

});


/* =========================
   FILE SELECTED
========================= */

fileInput.addEventListener("change", function () {

    const file = fileInput.files[0];

    if (!file) {
        return;
    }

    handleFile(file);

});


/* =========================
   DRAG & DROP
========================= */

uploadArea.addEventListener(
    "dragover",
    function (event) {

        event.preventDefault();

        uploadArea.classList.add("dragover");

    }
);


uploadArea.addEventListener(
    "dragleave",
    function () {

        uploadArea.classList.remove("dragover");

    }
);


uploadArea.addEventListener(
    "drop",
    function (event) {

        event.preventDefault();

        uploadArea.classList.remove("dragover");

        const file = event.dataTransfer.files[0];

        if (!file) {
            return;
        }

        handleFile(file);

    }
);


/* =========================
   HANDLE FILE
========================= */

function handleFile(file) {

    const allowedTypes = [
        "image/jpeg",
        "image/jpg",
        "image/png"
    ];

    const maxSize = 10 * 1024 * 1024;


    if (!allowedTypes.includes(file.type)) {

        alert(
            "Please upload a JPG, JPEG or PNG image."
        );

        return;
    }


    if (file.size > maxSize) {

        alert(
            "File size must be less than 10 MB."
        );

        return;
    }


    uploadArea.innerHTML = `
        <div class="upload-icon">✓</div>

        <h3>${file.name}</h3>

        <span>
            Image selected successfully
        </span>

        <button
            class="choose-btn"
            id="analyzeBtn"
        >
            Analyze Product →
        </button>

        <p class="file-info">
            ${formatFileSize(file.size)}
        </p>
    `;


    document
        .getElementById("analyzeBtn")
        .addEventListener(
            "click",
            function () {

                /*
                    Later this button will send
                    the image to the backend/OCR API.

                    For now it is only a frontend demo.
                */

                alert(
                    "Product image ready for analysis!"
                );

            }
        );

}


/* =========================
   FILE SIZE
========================= */

function formatFileSize(bytes) {

    if (bytes < 1024 * 1024) {

        return (
            (bytes / 1024).toFixed(1) +
            " KB"
        );

    }

    return (
        (bytes / (1024 * 1024)).toFixed(2) +
        " MB"
    );
}


/* =========================
   QUICK SCAN BUTTON
========================= */

const scanAction =
    document.getElementById("scanAction");

scanAction.addEventListener(
    "click",
    function () {

        document
            .getElementById("uploadArea")
            .scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

        setTimeout(function () {

            fileInput.click();

        }, 500);

    }
);


/* =========================
   SCAN NAVIGATION
========================= */

const scanNav =
    document.getElementById("scanNav");

scanNav.addEventListener(
    "click",
    function (event) {

        event.preventDefault();

        document
            .getElementById("uploadArea")
            .scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

    }
);


/* =========================
   CURRENT DATE
========================= */

const currentDate =
    document.getElementById("currentDate");

const today = new Date();

const dateOptions = {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric"
};

currentDate.textContent =
    today.toLocaleDateString(
        "en-IN",
        dateOptions
);