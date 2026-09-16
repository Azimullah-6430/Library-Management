```javascript
/* =========================================================
   LIBRACORE - COMMON JAVASCRIPT
========================================================= */


/* =========================================================
   DOM READY
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    initializeDate();

    initializeAlerts();

    initializeConfirmButtons();

    initializeMobileNavigation();

});


/* =========================================================
   CURRENT DATE
========================================================= */

function initializeDate() {

    const dateElement =
        document.getElementById("currentDate");

    if (!dateElement) {
        return;
    }


    const today = new Date();


    const options = {
        weekday: "short",
        year: "numeric",
        month: "short",
        day: "numeric"
    };


    dateElement.textContent =
        today.toLocaleDateString(
            "en-IN",
            options
        );

}


/* =========================================================
   AUTO HIDE ALERTS
========================================================= */

function initializeAlerts() {

    const alerts =
        document.querySelectorAll(
            ".alert"
        );


    alerts.forEach(function (alert) {

        setTimeout(function () {

            alert.style.transition =
                "opacity 0.4s ease";

            alert.style.opacity = "0";


            setTimeout(function () {

                alert.remove();

            }, 400);

        }, 4000);

    });

}


/* =========================================================
   CONFIRM BUTTONS
========================================================= */

function initializeConfirmButtons() {

    const buttons =
        document.querySelectorAll(
            "[data-confirm]"
        );


    buttons.forEach(function (button) {

        button.addEventListener(
            "click",
            function (event) {

                const message =
                    button.getAttribute(
                        "data-confirm"
                    );


                if (
                    message &&
                    !confirm(message)
                ) {

                    event.preventDefault();

                }

            }
        );

    });

}


/* =========================================================
   MOBILE NAVIGATION
========================================================= */

function initializeMobileNavigation() {

    const menuButton =
        document.getElementById(
            "mobileMenuButton"
        );

    const sidebar =
        document.querySelector(
            ".sidebar"
        );


    if (!menuButton || !sidebar) {
        return;
    }


    menuButton.addEventListener(
        "click",
        function () {

            sidebar.classList.toggle(
                "mobile-open"
            );

        }
    );

}


/* =========================================================
   FORM SUBMIT LOADING STATE
========================================================= */

function initializeFormLoading() {

    const forms =
        document.querySelectorAll(
            "form[data-loading]"
        );


    forms.forEach(function (form) {

        form.addEventListener(
            "submit",
            function () {

                const submitButton =
                    form.querySelector(
                        'button[type="submit"]'
                    );


                if (!submitButton) {
                    return;
                }


                submitButton.disabled = true;

                submitButton.dataset.originalText =
                    submitButton.textContent;

                submitButton.textContent =
                    "Processing...";

            }
        );

    });

}


/* =========================================================
   IMAGE FILE VALIDATION
========================================================= */

function validateImageFile(
    input
) {

    if (!input.files || !input.files[0]) {

        return true;

    }


    const file =
        input.files[0];


    const allowedTypes = [
        "image/png",
        "image/jpeg",
        "image/webp"
    ];


    if (!allowedTypes.includes(file.type)) {

        alert(
            "Invalid image format. Please select PNG, JPG, JPEG or WEBP."
        );

        input.value = "";

        return false;

    }


    /*
     * Maximum file size:
     * 5 MB
     */

    const maxSize =
        5 * 1024 * 1024;


    if (file.size > maxSize) {

        alert(
            "Image size must be less than 5 MB."
        );

        input.value = "";

        return false;

    }


    return true;

}


/* =========================================================
   IMAGE PREVIEW
========================================================= */

function previewImage(
    input,
    previewElement
) {

    if (
        !input.files ||
        !input.files[0]
    ) {

        return;

    }


    const file =
        input.files[0];


    const reader =
        new FileReader();


    reader.onload =
        function (event) {

            previewElement.src =
                event.target.result;

            previewElement.style.display =
                "block";

        };


    reader.readAsDataURL(file);

}


/* =========================================================
   NUMBER INPUT VALIDATION
========================================================= */

function validatePositiveNumber(
    input
) {

    const value =
        Number(input.value);


    if (
        Number.isNaN(value) ||
        value < 1
    ) {

        input.setCustomValidity(
            "Value must be at least 1."
        );

        return false;

    }


    input.setCustomValidity("");

    return true;

}


/* =========================================================
   BOOK COPY VALIDATION
========================================================= */

function validateCopies(
    input
) {

    const value =
        Number(input.value);


    if (
        Number.isNaN(value) ||
        value < 1
    ) {

        input.setCustomValidity(
            "Number of copies must be at least 1."
        );

        return false;

    }


    if (!Number.isInteger(value)) {

        input.setCustomValidity(
            "Number of copies must be a whole number."
        );

        return false;

    }


    input.setCustomValidity("");

    return true;

}


/* =========================================================
   SEARCH / FILTER HELPER
========================================================= */

function filterElements(
    input,
    selector,
    attributes
) {

    const searchValue =
        input.value
            .trim()
            .toLowerCase();


    const elements =
        document.querySelectorAll(
            selector
        );


    let visibleCount = 0;


    elements.forEach(function (element) {

        let matches = false;


        attributes.forEach(function (attribute) {

            const value =
                element.dataset[attribute] || "";


            if (
                value
                    .toLowerCase()
                    .includes(searchValue)
            ) {

                matches = true;

            }

        });


        if (matches) {

            element.style.display = "";

            visibleCount++;

        } else {

            element.style.display = "none";

        }

    });


    return visibleCount;

}


/* =========================================================
   DELETE CONFIRMATION
========================================================= */

function confirmDelete(
    itemName
) {

    return confirm(
        `Are you sure you want to delete "${itemName}"? This action cannot be undone.`
    );

}


/* =========================================================
   PRINT PAGE
========================================================= */

function printPage() {

    window.print();

}


/* =========================================================
   GO BACK
========================================================= */

function goBack() {

    window.history.back();

}


/* =========================================================
   SCROLL TO TOP
========================================================= */

function scrollToTop() {

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


/* =========================================================
   CHARACTER COUNTER
========================================================= */

function initializeCharacterCounter(
    input,
    counter,
    maxLength
) {

    if (!input || !counter) {
        return;
    }


    function updateCounter() {

        const length =
            input.value.length;


        counter.textContent =
            `${length}/${maxLength}`;


        if (length >= maxLength) {

            counter.style.color =
                "#dc2626";

        } else {

            counter.style.color =
                "";

        }

    }


    input.addEventListener(
        "input",
        updateCounter
    );


    updateCounter();

}


/* =========================================================
   GLOBAL IMAGE ERROR HANDLER
========================================================= */

document.addEventListener(
    "error",
    function (event) {

        if (
            event.target &&
            event.target.tagName === "IMG"
        ) {

            event.target.style.display =
                "none";

        }

    },
    true
);
```
