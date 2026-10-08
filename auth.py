from flask import Blueprint, render_template, request

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    errors = []

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name:
            errors.append("Name is required")
        if not email:
            errors.append("Email is required")
        if not password:
            errors.append("Password is required")
        if not confirm_password:
            errors.append("Confirm password is required")

        if password and confirm_password and password != confirm_password:
            errors.append("Passwords do not match")

        if len(name) > 100:
            errors.append("Name is too long (100 characters maximum)")

        if len(email) > 255:
            errors.append("Email is too long (255 characters maximum)")

        if len(password.encode("utf-8")) > 72:
            errors.append("Password is too long (72 bytes maximum)")

    return render_template("register.html", errors=errors)