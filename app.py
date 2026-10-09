import os
import secrets

from cachelib import SimpleCache
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session

from auth import auth, login_required
from db import get_database_tls_options
from todos import todos

load_dotenv()

APP_ENV = os.environ.get("APP_ENV", "development").strip().lower()
if APP_ENV not in {"development", "production"}:
    raise RuntimeError("APP_ENV must be 'development' or 'production'")
get_database_tls_options()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ["SECRET_KEY"],
    SESSION_TYPE="cachelib",
    SESSION_CACHELIB=SimpleCache(),
    SESSION_PERMANENT=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=APP_ENV == "production",
)

Session(app)
app.register_blueprint(auth)
app.register_blueprint(todos)


@app.context_processor
def inject_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)

    return {"csrf_token": session["csrf_token"]}


@app.before_request
def check_csrf_token():
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        expected = session.get("csrf_token", "")
        submitted = request.form.get("csrf_token", "")

        if (
            not expected
            or not submitted
            or not secrets.compare_digest(
                expected.encode("utf-8"),
                submitted.encode("utf-8"),
            )
        ):
            return render_template("csrf_error.html"), 400


@app.get("/")
@login_required
def home():
    return redirect(url_for("todos.index"))


@app.errorhandler(404)
def not_found(error):
    return render_template(
        "error.html",
        code=404,
        heading="This page or to-do isn't available",
        message="It may have been deleted, or the link may be incorrect.",
    ), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return render_template(
        "error.html",
        code=405,
        heading="Please use the form on the page",
        message="Reopen the page and use its buttons to make this change.",
    ), 405


@app.errorhandler(500)
def server_error(error):
    return render_template(
        "error.html",
        code=500,
        heading="Something went wrong",
        message="Please reopen the page and try again in a moment.",
    ), 500
