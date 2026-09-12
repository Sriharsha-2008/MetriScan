const loginForm = document.getElementById("loginForm");

const email = document.getElementById("email");

const password = document.getElementById("password");

const error = document.getElementById("error");

const showPassword =
    document.getElementById("showPassword");


/* =========================
   SHOW / HIDE PASSWORD
========================= */

showPassword.addEventListener("click", function () {

    if (password.type === "password") {

        password.type = "text";

        showPassword.textContent = "Hide";

    } else {

        password.type = "password";

        showPassword.textContent = "Show";
    }

});


/* =========================
   ERROR FUNCTION
========================= */

function showError(message) {

    error.textContent = message;

    error.style.display = "block";
}


/* =========================
   LOGIN VALIDATION
========================= */

loginForm.addEventListener("submit", function (event) {

    event.preventDefault();

    const emailValue = email.value.trim();

    const passwordValue = password.value;


    /* Empty fields */

    if (
        emailValue === "" ||
        passwordValue === ""
    ) {

        showError(
            "Please enter your email and password."
        );

        return;
    }


    /* Password length */

    if (passwordValue.length < 6) {

        showError(
            "Password must contain at least 6 characters."
        );

        return;
    }


    /* Valid frontend input */

    error.style.display = "none";


    /*
       Frontend demo only.

       Real authentication will be connected
       to the backend later.
    */

    alert("Login successful!");

});