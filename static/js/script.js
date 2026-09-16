document.addEventListener("DOMContentLoaded", function () {

    /* =========================================
       MOBILE SIDEBAR
    ========================================= */

    const sidebar = document.querySelector(".sidebar");
    const sidebarOverlay = document.querySelector(".sidebar-overlay");

    const menuButtons = document.querySelectorAll(
        ".mobile-menu-button, .sidebar-toggle"
    );

    function openSidebar() {
        if (!sidebar) return;

        sidebar.classList.add("open");

        if (sidebarOverlay) {
            sidebarOverlay.classList.add("active");
        }

        document.body.style.overflow = "hidden";
    }

    function closeSidebar() {
        if (!sidebar) return;

        sidebar.classList.remove("open");

        if (sidebarOverlay) {
            sidebarOverlay.classList.remove("active");
        }

        document.body.style.overflow = "";
    }

    menuButtons.forEach(function (button) {
        button.addEventListener("click", function () {

            if (sidebar && sidebar.classList.contains("open")) {
                closeSidebar();
            } else {
                openSidebar();
            }

        });
    });

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


    /* =========================================
       PASSWORD VISIBILITY
    ========================================= */

    document.querySelectorAll(".password-toggle").forEach(function (button) {

        button.addEventListener("click", function () {

            const targetId = button.dataset.target;

            if (!targetId) return;

            const input = document.getElementById(targetId);

            if (!input) return;

            if (input.type === "password") {
                input.type = "text";
                button.setAttribute("aria-label", "Hide password");
            } else {
                input.type = "password";
                button.setAttribute("aria-label", "Show password");
            }

        });

    });


    /* =========================================
       FLASH MESSAGE AUTO HIDE
    ========================================= */

    document.querySelectorAll(".flash-message").forEach(function (message) {

        setTimeout(function () {

            message.style.opacity = "0";
            message.style.transform = "translateX(20px)";
            message.style.transition =
                "opacity 0.3s ease, transform 0.3s ease";

            setTimeout(function () {
                message.remove();
            }, 300);

        }, 4500);

    });


    /* =========================================
       IMAGE PREVIEW
    ========================================= */

    document.querySelectorAll(
        'input[type="file"][data-preview]'
    ).forEach(function (input) {

        input.addEventListener("change", function () {

            const previewId = input.dataset.preview;
            const preview = document.getElementById(previewId);

            if (!preview) return;

            const image = preview.querySelector("img");

            if (!input.files || !input.files.length) {
                preview.hidden = true;

                if (image) {
                    image.src = "";
                }

                return;
            }

            const file = input.files[0];

            if (!file.type.startsWith("image/")) {
                alert("Please select a valid image file.");
                input.value = "";
                preview.hidden = true;
                return;
            }

            const reader = new FileReader();

            reader.onload = function (event) {

                if (image) {
                    image.src = event.target.result;
                }

                preview.hidden = false;

                const uploadBox =
                    input.closest(".upload-box");

                if (uploadBox) {
                    const content =
                        uploadBox.querySelector(".upload-content");

                    if (content) {
                        content.style.display = "none";
                    }
                }

            };

            reader.readAsDataURL(file);

        });

    });


    /* =========================================
       REMOVE IMAGE
    ========================================= */

    document.querySelectorAll(".remove-image").forEach(function (button) {

        button.addEventListener("click", function (event) {

            event.preventDefault();
            event.stopPropagation();

            const inputId = button.dataset.input;
            const previewId = button.dataset.preview;

            const input =
                inputId ? document.getElementById(inputId) : null;

            const preview =
                previewId ? document.getElementById(previewId) : null;

            if (input) {
                input.value = "";
            }

            if (preview) {

                preview.hidden = true;

                const image = preview.querySelector("img");

                if (image) {
                    image.src = "";
                }

                const uploadBox =
                    preview.closest(".upload-box");

                if (uploadBox) {

                    const content =
                        uploadBox.querySelector(".upload-content");

                    if (content) {
                        content.style.display = "";
                    }

                }

            }

        });

    });


    /* =========================================
       DRAG & DROP UPLOAD
    ========================================= */

    document.querySelectorAll(".upload-box").forEach(function (box) {

        const input = box.querySelector('input[type="file"]');

        if (!input) return;

        box.addEventListener("dragover", function (event) {

            event.preventDefault();

            box.classList.add("dragover");

        });

        box.addEventListener("dragleave", function (event) {

            event.preventDefault();

            box.classList.remove("dragover");

        });

        box.addEventListener("drop", function (event) {

            event.preventDefault();

            box.classList.remove("dragover");

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

                input.dispatchEvent(
                    new Event("change", {
                        bubbles: true
                    })
                );

            } catch (error) {

                console.error(
                    "Unable to process dropped image:",
                    error
                );

            }

        });

        box.addEventListener("click", function (event) {

            if (
                event.target.closest(".remove-image") ||
                event.target.closest(".upload-browse")
            ) {
                return;
            }

            input.click();

        });

    });


    /* =========================================
       DELETE CONFIRMATION
    ========================================= */

    document.querySelectorAll("[data-confirm-delete]").forEach(
        function (element) {

            element.addEventListener("click", function (event) {

                const message =
                    element.dataset.confirmDelete ||
                    "Are you sure you want to delete this book?";

                if (!window.confirm(message)) {
                    event.preventDefault();
                }

            });

        }
    );


    /* =========================================
       MODAL DELETE CONFIRMATION
    ========================================= */

    document.querySelectorAll(".confirm-delete").forEach(
        function (button) {

            button.addEventListener("click", function (event) {

                event.preventDefault();

                const modalId = button.dataset.modal;

                if (!modalId) return;

                const modal =
                    document.getElementById(modalId);

                if (modal) {
                    modal.classList.add("active");
                }

            });

        }
    );

    document.querySelectorAll(".modal-overlay").forEach(
        function (modal) {

            modal.addEventListener("click", function (event) {

                if (event.target === modal) {
                    modal.classList.remove("active");
                }

            });

        }
    );

    document.querySelectorAll("[data-close-modal]").forEach(
        function (button) {

            button.addEventListener("click", function () {

                const modal =
                    button.closest(".modal-overlay");

                if (modal) {
                    modal.classList.remove("active");
                }

            });

        }
    );


    /* =========================================
       SEARCH CLEAR
    ========================================= */

    document.querySelectorAll("[data-clear-search]").forEach(
        function (button) {

            button.addEventListener("click", function () {

                const targetId =
                    button.dataset.clearSearch;

                const input =
                    document.getElementById(targetId);

                if (!input) return;

                input.value = "";
                input.focus();

            });

        }
    );


    /* =========================================
       KEYBOARD SEARCH SHORTCUT
    ========================================= */

    document.addEventListener("keydown", function (event) {

        if (
            (event.ctrlKey || event.metaKey) &&
            event.key.toLowerCase() === "k"
        ) {

            const searchInput =
                document.querySelector(
                    'input[type="search"], .search-input'
                );

            if (searchInput) {

                event.preventDefault();

                searchInput.focus();
                searchInput.select();

            }

        }

        if (event.key === "Escape") {

            closeSidebar();

            document.querySelectorAll(".modal-overlay.active")
                .forEach(function (modal) {
                    modal.classList.remove("active");
                });

        }

    });


    /* =========================================
       PREVENT DOUBLE FORM SUBMISSION
    ========================================= */

    document.querySelectorAll("form").forEach(function (form) {

        form.addEventListener("submit", function () {

            if (
                form.dataset.preventDoubleSubmit === "false"
            ) {
                return;
            }

            if (form.dataset.submitted === "true") {
                return;
            }

            form.dataset.submitted = "true";

            const submitButtons =
                form.querySelectorAll(
                    'button[type="submit"], input[type="submit"]'
                );

            submitButtons.forEach(function (button) {

                if (!button.disabled) {

                    button.dataset.originalText =
                        button.textContent;

                    button.disabled = true;

                    if (button.tagName === "BUTTON") {
                        button.textContent = "Processing...";
                    }

                }

            });

        });

    });


    /* =========================================
       RESPONSIVE SIDEBAR RESET
    ========================================= */

    window.addEventListener("resize", function () {

        if (window.innerWidth > 900) {
            closeSidebar();
        }

    });


    /* =========================================
       IMAGE ERROR HANDLING
    ========================================= */

    document.querySelectorAll("img").forEach(function (image) {

        image.addEventListener("error", function () {

            image.classList.add("image-load-error");

        });

    });


    /* =========================================
       TABLE ROW KEYBOARD ACCESS
    ========================================= */

    document.querySelectorAll(
        "tr[data-href]"
    ).forEach(function (row) {

        row.setAttribute("tabindex", "0");

        row.addEventListener("click", function () {

            const url = row.dataset.href;

            if (url) {
                window.location.href = url;
            }

        });

        row.addEventListener("keydown", function (event) {

            if (
                event.key === "Enter" ||
                event.key === " "
            ) {

                event.preventDefault();

                const url = row.dataset.href;

                if (url) {
                    window.location.href = url;
                }

            }

        });

    });


    /* =========================================
       ACCESSIBILITY
    ========================================= */

    document.querySelectorAll(
        "[title]"
    ).forEach(function (element) {

        if (!element.getAttribute("aria-label")) {

            const title =
                element.getAttribute("title");

            if (title) {
                element.setAttribute(
                    "aria-label",
                    title
                );
            }

        }

    });

});
