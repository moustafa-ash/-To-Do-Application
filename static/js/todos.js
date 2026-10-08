document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-title-form]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const input = form.querySelector("[data-title-input]");
            const error = form.querySelector("[data-title-error]");
            const value = input.value.trim();

            if (!value) {
                event.preventDefault();
                error.textContent = "Title is required";
                input.focus();
            } else if (value.length > 200) {
                event.preventDefault();
                error.textContent = "Title is too long";
                input.focus();
            } else {
                error.textContent = "";
            }
        });
    });

    document.querySelectorAll("[data-delete-form]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!window.confirm("Delete this to-do? This cannot be undone.")) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll("[data-edit-link]").forEach((link) => {
        link.addEventListener("click", (event) => {
            event.preventDefault();
            const url = new URL(window.location.href);
            url.searchParams.set("edit", link.dataset.editLink);
            window.location.assign(url);
        });
    });
});
