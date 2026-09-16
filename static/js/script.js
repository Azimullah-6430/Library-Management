document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       MOBILE SIDEBAR
       ===================================================== */

    const menuButton = document.querySelector(".mobile-menu-button");
    const sidebar = document.querySelector(".sidebar");
    const sidebarOverlay = document.querySelector(".sidebar-overlay");

    function openSidebar() {
        if (sidebar) sidebar.classList.add("open");
        if (sidebarOverlay) sidebarOverlay.classList.add("visible");
    }

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove("open");
        if (sidebarOverlay) sidebarOverlay.classList.remove("visible");
    }

    if (menuButton) {
        menuButton.addEventListener("click", function () {
            if (sidebar && sidebar.classList.contains("open")) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener("click", closeSidebar);
    }

    document.querySelectorAll(".nav-item").forEach(function (item) {
        item.addEventListener("click", function () {
            if (window.innerWidth <= 900) {
                closeSidebar();
            }
        });
    });


    /* =====================================================
       PASSWORD VISIBILITY
       ===================================================== */

    document.querySelectorAll(".password-toggle").forEach(function (button) {

        button.addEventListener("click", function () {

            const targetId = button.getAttribute("data-target");
            const input = document.getElementById(targetId);

            if (!input) return;

            if (input.type === "password") {
                input.type = "text";

                const icon = button.querySelector("i");

                if (icon) {
                    icon.classList.remove("bi-eye");
                    icon.classList.add("bi-eye-slash");
                }

            } else {
                input.type = "password";

                const icon = button.querySelector("i");

                if (icon) {
                    icon.classList.remove("bi-eye-slash");
                    icon.classList.add("bi-eye");
                }
            }
        });

    });


    /* =====================================================
       AUTO HIDE FLASH MESSAGES
       ===================================================== */

    const flashMessages = document.querySelectorAll(".flash-message");

    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";
            message.style.transform = "translateX(15px)";
            message.style.transition = "opacity 250ms ease, transform 250ms ease";

            setTimeout(function () {
                message.remove();
            }, 300);

        }, 4500);

    });


    /* =====================================================
       IMAGE UPLOAD PREVIEW
       ===================================================== */

    document.querySelectorAll('input[type="file"]').forEach(function (input) {

        input.addEventListener("change", function () {

            const file = input.files && input.files[0];

            if (!file) return;

            if (!file.type.startsWith("image/")) {
                alert("Please select a valid image file.");
                input.value = "";
                return;
            }

            const previewId = input.getAttribute("data-preview");

            if (!previewId) return;

            const preview = document.getElementById(previewId);

            if (!preview) return;

            const image = preview.querySelector("img");

            if (!image) return;

            const reader = new FileReader();

            reader.onload = function (event) {

                image.src = event.target.result;

                preview.classList.add("visible");

                const uploadBox = input.closest(".upload-box");

                if (uploadBox) {
                    uploadBox.classList.add("has-image");
                }

            };

            reader.readAsDataURL(file);

        });

    });


    /* =====================================================
       REMOVE IMAGE
       ===================================================== */

    document.querySelectorAll(".remove-image").forEach(function (button) {

        button.addEventListener("click", function (event) {

            event.preventDefault();
            event.stopPropagation();

            const previewId = button.getAttribute("data-preview");

            const preview = document.getElementById(previewId);

            if (!preview) return;

            const inputId = preview.getAttribute("data-input");
            const input = document.getElementById(inputId);

            if (input) {
                input.value = "";
            }

            preview.classList.remove("visible");

            const image = preview.querySelector("img");

            if (image) {
                image.removeAttribute("src");
            }

            const uploadBox = preview.closest(".upload-box");

            if (uploadBox) {
                uploadBox.classList.remove("has-image");
            }

        });

    });


    /* =====================================================
       DRAG AND DROP IMAGE UPLOAD
       ===================================================== */

    document.querySelectorAll(".upload-box").forEach(function (box) {

        const input = box.querySelector('input[type="file"]');

        if (!input) return;

        ["dragenter", "dragover"].forEach(function (eventName) {

            box.addEventListener(eventName, function (event) {

                event.preventDefault();
                event.stopPropagation();

                box.style.borderColor = "var(--navy-700)";
                box.style.background = "#f5f8fb";

            });

        });

        ["dragleave", "drop"].forEach(function (eventName) {

            box.addEventListener(eventName, function (event) {

                event.preventDefault();
                event.stopPropagation();

                box.style.borderColor = "";
                box.style.background = "";

            });

        });

        box.addEventListener("drop", function (event) {

            const files = event.dataTransfer.files;

            if (!files || !files.length) return;

            const file = files[0];

            if (!file.type.startsWith("image/")) {
                alert("Please drop a valid image file.");
                return;
            }

            try {

                const dataTransfer = new DataTransfer();

                dataTransfer.items.add(file);

                input.files = dataTransfer.files;

                input.dispatchEvent(new Event("change", {
                    bubbles: true
                }));

            } catch (error) {

                console.warn(
                    "Browser does not allow programmatic file assignment.",
                    error
                );

            }

        });

    });


    /* =====================================================
       CONFIRM DELETE ACTIONS
       ===================================================== */

    document.querySelectorAll("[data-confirm-delete]").forEach(function (button) {

        button.addEventListener("click", function (event) {

            const message =
                button.getAttribute("data-confirm-delete") ||
                "Are you sure you want to delete this book?";

            if (!window.confirm(message)) {
                event.preventDefault();
            }

        });

    });


    /* =====================================================
       SEARCH INPUT CLEAR
       ===================================================== */

    document.querySelectorAll(".clear-search").forEach(function (button) {

        button.addEventListener("click", function () {

            const targetId = button.getAttribute("data-target");

            const input = document.getElementById(targetId);

            if (!input) return;

            input.value = "";

            const form = input.closest("form");

            if (form) {
                form.submit();
            }

        });

    });


    /* =====================================================
       SEARCH KEYBOARD SHORTCUT
       ===================================================== */

    document.addEventListener("keydown", function (event) {

        if (
            (event.ctrlKey || event.metaKey) &&
            event.key.toLowerCase() === "k"
        ) {

            const searchInput =
                document.querySelector(".search-input-wrapper input");

            if (searchInput) {
                event.preventDefault();
                searchInput.focus();
            }

        }

    });


    /* =====================================================
       PREVENT DOUBLE FORM SUBMISSION
       ===================================================== */

    document.querySelectorAll("form").forEach(function (form) {

        form.addEventListener("submit", function () {

            if (form.dataset.submitting === "true") {
                return;
            }

            form.dataset.submitting = "true";

            const submitButtons =
                form.querySelectorAll(
                    'button[type="submit"], input[type="submit"]'
                );

            submitButtons.forEach(function (button) {

                button.disabled = true;

                const originalText =
                    button.innerHTML || button.value;

                button.dataset.originalText = originalText;

                if (button.tagName.toLowerCase() === "button") {

                    if (!button.querySelector(".button-loader")) {

                        button.innerHTML =
                            '<i class="bi bi-arrow-repeat spin"></i> ' +
                            "Processing...";

                    }

                } else {
                    button.value = "Processing...";
                }

            });

        });

    });


    /* =====================================================
       SMOOTH SCROLL FOR INTERNAL ANCHORS
       ===================================================== */

    document.querySelectorAll('a[href^="#"]').forEach(function (link) {

        link.addEventListener("click", function (event) {

            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") return;

            const target = document.querySelector(targetId);

            if (!target) return;

            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        });

    });


    /* =====================================================
       RESPONSIVE SIDEBAR RESET
       ===================================================== */

    window.addEventListener("resize", function () {

        if (window.innerWidth > 900) {
            closeSidebar();
        }

    });


    /* =====================================================
       IMAGE ERROR HANDLING
       ===================================================== */

    document.querySelectorAll("img").forEach(function (image) {

        image.addEventListener("error", function () {

            if (image.dataset.errorHandled === "true") {
                return;
            }

            image.dataset.errorHandled = "true";

            image.style.display = "none";

            const parent = image.parentElement;

            if (parent && !parent.querySelector(".image-error-placeholder")) {

                const placeholder =
                    document.createElement("div");

                placeholder.className =
                    "image-error-placeholder large-image-placeholder";

                placeholder.innerHTML =
                    '<i class="bi bi-image"></i>' +
                    '<span>Image unavailable</span>';

                parent.appendChild(placeholder);

            }

        });

    });


    /* =====================================================
       TABLE ROW KEYBOARD ACCESS
       ===================================================== */

    document.querySelectorAll(".library-table tbody tr").forEach(function (row) {

        const link = row.querySelector("a");

        if (!link) return;

        row.setAttribute("tabindex", "0");

        row.addEventListener("keydown", function (event) {

            if (event.key === "Enter") {
                link.click();
            }

        });

    });


    /* =====================================================
       TOOLTIP INITIALIZATION
       ===================================================== */

    document.querySelectorAll("[title]").forEach(function (element) {

        element.addEventListener("mouseenter", function () {

            element.setAttribute(
                "aria-label",
                element.getAttribute("title")
            );

        });

    });

});
