const form = document.querySelector("form[data-auth]");

if (form) {
    form.addEventListener("submit", (event) => {
        const values = Object.fromEntries(new FormData(form));
        const registering = form.dataset.auth === "register";
        const fields = registering
            ? [["name", "Name"], ["email", "Email"], ["password", "Password"],
                ["confirm_password", "Confirm password"]]
            : [["email", "Email"], ["password", "Password"]];
        const errors = [];

        for (const [field, label] of fields) {
            const value = field === "name" || field === "email"
                ? values[field].trim() : values[field];
            if (!value) errors.push([field, `${label} is required`]);
        }

        if (registering) {
            if (values.password && values.confirm_password &&
                values.password !== values.confirm_password) {
                errors.push(["confirm_password", "Passwords do not match"]);
            }
            if ([...values.name.trim()].length > 100) {
                errors.push(["name", "Name is too long (100 characters maximum)"]);
            }
            if ([...values.email.trim()].length > 255) {
                errors.push(["email", "Email is too long (255 characters maximum)"]);
            }
        }

        if (new TextEncoder().encode(values.password).length > 72) {
            errors.push(["password", registering
                ? "Password is too long (72 bytes maximum)"
                : "Invalid email or password"]);
        }

        document.getElementById("form-errors").replaceChildren(
            ...errors.map(([, message]) => {
                const item = document.createElement("li");
                item.textContent = message;
                return item;
            }),
        );

        if (errors.length) {
            event.preventDefault();
            form.elements.namedItem(errors[0][0]).focus();
        }
    });
}
