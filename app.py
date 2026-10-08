import os
import secrets

from cachelib import SimpleCache
from dotenv import load_dotenv
from flask import Flask, render_template, request, session
from flask_session import Session

from auth import auth, login_required

load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ["SECRET_KEY"],
    SESSION_TYPE="cachelib",
    SESSION_CACHELIB=SimpleCache(),
    SESSION_PERMANENT=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

Session(app)
app.register_blueprint(auth)


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
    return "To-Do application is running"
