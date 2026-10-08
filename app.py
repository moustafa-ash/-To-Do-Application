import os

from cachelib import SimpleCache
from dotenv import load_dotenv
from flask import Flask
from flask_session import Session

from auth import auth

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


@app.get("/")
def home():
    return "To-Do application is running"
