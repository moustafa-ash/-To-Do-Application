import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from pymysql.constants import CLIENT

load_dotenv()


def get_database_tls_options():
    app_env = os.environ.get("APP_ENV", "development").strip().lower()
    if app_env == "development":
        return {}
    if app_env != "production":
        raise RuntimeError("APP_ENV must be 'development' or 'production'")

    ca_file = os.environ.get("DB_SSL_CA", "")
    if not ca_file or not Path(ca_file).is_file():
        raise RuntimeError(
            "APP_ENV=production requires DB_SSL_CA to name an available CA certificate file"
        )

    return {
        "ssl_ca": ca_file,
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
    }


def get_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        # Matched rows count as success even when the submitted value is unchanged.
        client_flag=CLIENT.FOUND_ROWS,
        **get_database_tls_options(),
    )
