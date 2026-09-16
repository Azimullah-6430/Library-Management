/* ============================================================
   CRESCENT COLLEGE LIBRARY MANAGEMENT SYSTEM
   Global JavaScript
   ============================================================ */

"use strict";


/* ============================================================
   DOM READY
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeSidebar();

        initializeDeleteConfirmation();

        initializeSearchShortcut();

        initializeCardAnimations();

        initializeAutoDismissMessages();

        initializeButtonProtection();

    }
);


/* ============================================================
   SIDEBAR / MOBILE NAVIGATION
   ============================================================ */

function initializeSidebar() {

    const menuButton =
        document.getElementById(
            "mobileMenuButton"
        );

    const sidebar =
        document.getElementById(
            "sidebar"
        );

    const overlay =
        document.getElementById(
            "sidebarOverlay"
        );

    const closeButton =
        document.getElementById(
            "closeSidebarButton"
        );


    if (!sidebar) {
        return;
    }


    function openSidebar() {

        sidebar.classList.add(
            "sidebar-open"
        );


        if (overlay) {

            overlay.classList.add(
                "overlay-visible"
            );

        }


        document.body.classList.add(
            "sidebar-active"
        );

    }


    function closeSidebar() {

        sidebar.classList.remove(
            "sidebar-open"
        );


        if (overlay) {

            overlay.classList.remove(
                "overlay-visible"
            );

        }


        document.body.classList.remove(
            "sidebar-active"
        );

    }


    if (menuButton) {

        menuButton.addEventListener(
            "click",
            openSidebar
        );

    }


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeSidebar
        );

    }


    if (overlay) {

        overlay.addEventListener(
            "click",
            closeSidebar
        );

    }


    /* Close sidebar after navigation */

    const sidebarLinks =
        sidebar.querySelectorAll(
            "a"
        );


    sidebarLinks.forEach(
        function (link) {

            link.addEventListener(
                "click",
                function () {

                    if (
                        window.innerWidth <= 900
                    ) {

                        closeSidebar();

                    }

                }
            );

        }
    );


    /* Escape key */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape"
            ) {

                closeSidebar();

            }

        }
    );


    /* Handle resize */

    window.addEventListener(
        "resize",
        function () {

            if (
                window.innerWidth > 900
            ) {

                closeSidebar();

            }

        }
    );

}


/* ============================================================
   DELETE CONFIRMATION
   ============================================================ */

function initializeDeleteConfirmation() {

    const deleteForms =
        document.querySelectorAll(
            'form[action*="/delete-book/"]'
        );


    deleteForms.forEach(
        function (form) {

            if (
                form.dataset.deleteInitialized ===
                "true"
            ) {

                return;

            }


            form.dataset.deleteInitialized =
                "true";


            form.addEventListener(
                "submit",
                function (event) {

                    const confirmed =
                        window.confirm(
                            "Are you sure you want to permanently delete this book from the library catalogue?"
                        );


                    if (!confirmed) {

                        event.preventDefault();

                        return;

                    }


                    const button =
                        form.querySelector(
                            "button[type='submit']"
                        );


                    if (button) {

                        button.disabled =
                            true;

                        button.textContent =
                            "Deleting...";

                    }

                }
            );

        }
    );

}


/* ============================================================
   GLOBAL SEARCH SHORTCUT
   ============================================================ */

function initializeSearchShortcut() {

    document.addEventListener(
        "keydown",
        function (event) {

            /*
             * Ctrl + K
             * or
             * Cmd + K
             */

            if (
                (
                    event.ctrlKey ||
                    event.metaKey
                )
                &&
                event.key.toLowerCase() === "k"
            ) {

                event.preventDefault();


                const searchInput =
                    document.querySelector(
                        'input[name="search"], #searchInput'
                    );


                if (searchInput) {

                    searchInput.focus();

                    searchInput.select();

                }

            }

        }
    );

}


/* ============================================================
   CARD ANIMATIONS
   ============================================================ */

function initializeCardAnimations() {

    const animatedElements =
        document.querySelectorAll(
            `
            .stat-card,
            .book-card,
            .action-card,
            .info-action-card,
            .section-card
            `
        );


    if (
        !animatedElements.length
    ) {

        return;

    }


    /*
     * Use IntersectionObserver where available.
     * This prevents unnecessary animation work for
     * elements that are not currently visible.
     */

    if (
        "IntersectionObserver" in window
    ) {

        const observer =
            new IntersectionObserver(
                function (entries) {

                    entries.forEach(
                        function (entry) {

                            if (
                                entry.isIntersecting
                            ) {

                                entry.target.classList.add(
                                    "element-visible"
                                );

                                observer.unobserve(
                                    entry.target
                                );

                            }

                        }
                    );

                },
                {
                    threshold: 0.08
                }
            );


        animatedElements.forEach(
            function (element) {

                observer.observe(
                    element
                );

            }
        );

    } else {

        animatedElements.forEach(
            function (element) {

                element.classList.add(
                    "element-visible"
                );

            }
        );

    }

}


/* ============================================================
   FLASH MESSAGE AUTO DISMISS
   ============================================================ */

function initializeAutoDismissMessages() {

    const messages =
        document.querySelectorAll(
            ".alert, .flash-message"
        );


    messages.forEach(
        function (message) {

            /*
             * Login flash messages are intentionally
             * kept visible.
             */

            if (
                message.closest(
                    ".login-page"
                )
            ) {

                return;

            }


            setTimeout(
                function () {

                    message.classList.add(
                        "message-hiding"
                    );


                    setTimeout(
                        function () {

                            if (
                                message.parentNode
                            ) {

                                message.remove();

                            }

                        },
                        350
                    );

                },
                5000
            );

        }
    );

}


/* ============================================================
   PREVENT DOUBLE SUBMISSION
   ============================================================ */

function initializeButtonProtection() {

    const forms =
        document.querySelectorAll(
            "form"
        );


    forms.forEach(
        function (form) {

            /*
             * Delete forms are handled separately.
             */

            if (
                form.action.includes(
                    "/delete-book/"
                )
            ) {

                return;

            }


            form.addEventListener(
                "submit",
                function () {

                    const submitButtons =
                        form.querySelectorAll(
                            'button[type="submit"], input[type="submit"]'
                        );


                    submitButtons.forEach(
                        function (button) {

                            /*
                             * Do not disable buttons that
                             * are already disabled.
                             */

                            if (
                                button.disabled
                            ) {

                                return;

                            }


                            button.dataset.originalText =
                                button.textContent;


                            button.disabled =
                                true;


                            if (
                                button.tagName ===
                                "BUTTON"
                            ) {

                                button.innerHTML =
                                    `
                                    <span class="button-loading">
                                        ⏳
                                    </span>
                                    Processing...
                                    `;

                            }

                        }
                    );

                }
            );

        }
    );

}


/* ============================================================
   NUMBER INPUT SAFETY
   ============================================================ */

document.addEventListener(
    "input",
    function (event) {

        const element =
            event.target;


        if (
            !element.matches(
                'input[type="number"]'
            )
        ) {

            return;

        }


        /*
         * Prevent negative values from being
         * accidentally entered.
         */

        if (
            element.value !== ""
            &&
            Number(element.value) < 0
        ) {

            element.value =
                0;

        }

    }
);


/* ============================================================
   IMAGE ERROR HANDLING
   ============================================================ */

document.addEventListener(
    "error",
    function (event) {

        const image =
            event.target;


        if (
            image.tagName !== "IMG"
        ) {

            return;

        }


        /*
         * Prevent repeated error events.
         */

        if (
            image.dataset.imageErrorHandled ===
            "true"
        ) {

            return;

        }


        image.dataset.imageErrorHandled =
            "true";


        /*
         * Hide broken book-cover images
         * instead of displaying a broken-image icon.
         */

        if (
            image.classList.contains(
                "book-cover"
            )
            ||
            image.classList.contains(
                "book-cover-large"
            )
        ) {

            image.style.display =
                "none";

        }

    },
    true
);


/* ============================================================
   SEARCH FORM UX
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const searchForms =
            document.querySelectorAll(
                ".catalogue-search-form"
            );


        searchForms.forEach(
            function (form) {

                const input =
                    form.querySelector(
                        'input[name="search"]'
                    );


                if (!input) {
                    return;
                }


                /*
                 * Clear search with Escape.
                 */

                input.addEventListener(
                    "keydown",
                    function (event) {

                        if (
                            event.key ===
                            "Escape"
                        ) {

                            input.value =
                                "";

                        }

                    }
                );

            }
        );

    }
);


/* ============================================================
   ACTIVE NAVIGATION
   ============================================================ */

function initializeActiveNavigation() {

    const currentPath =
        window.location.pathname;


    const navigationLinks =
        document.querySelectorAll(
            ".sidebar a[href]"
        );


    navigationLinks.forEach(
        function (link) {

            const href =
                link.getAttribute(
                    "href"
                );


            if (
                !href
                ||
                href === "#"
            ) {

                return;

            }


            /*
             * Remove query strings before comparison.
             */

            const linkPath =
                href.split("?")[0];


            if (
                linkPath === currentPath
            ) {

                link.classList.add(
                    "active"
                );

            }

        }
    );

}


document.addEventListener(
    "DOMContentLoaded",
    initializeActiveNavigation
);


/* ============================================================
   TABLE / CARD HOVER ACCESSIBILITY
   ============================================================ */

document.addEventListener(
    "keydown",
    function (event) {

        /*
         * Allow keyboard users to activate elements
         * that have role="button".
         */

        if (
            event.key !== "Enter"
            &&
            event.key !== " "
        ) {

            return;

        }


        const target =
            event.target;


        if (
            target.getAttribute(
                "role"
            ) !== "button"
        ) {

            return;

        }


        event.preventDefault();

        target.click();

    }
);


/* ============================================================
   UTILITY: SAFE TEXT
   ============================================================ */

function escapeHTML(value) {

    if (
        value === null
        ||
        value === undefined
    ) {

        return "";

    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );

}


/* ============================================================
   UTILITY: FORMAT NUMBER
   ============================================================ */

function formatNumber(value) {

    const number =
        Number(value);


    if (
        Number.isNaN(number)
    ) {

        return "0";

    }


    return number.toLocaleString(
        "en-IN"
    );

}


/* ============================================================
   GLOBAL API HELPERS
   ============================================================ */

async function fetchJSON(
    url,
    options = {}
) {

    const response =
        await fetch(
            url,
            options
        );


    const contentType =
        response.headers.get(
            "content-type"
        ) || "";


    if (
        !contentType.includes(
            "application/json"
        )
    ) {

        throw new Error(
            "Server returned a non-JSON response."
        );

    }


    const data =
        await response.json();


    if (!response.ok) {

        throw new Error(
            data.error ||
            data.message ||
            "Request failed."
        );

    }


    return data;

}


/* ============================================================
   CONSOLE STATUS
   ============================================================ */

console.log(
    "Crescent College Library Management System loaded."
);
