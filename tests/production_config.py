import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from db import get_connection, get_database_tls_options


def production_environment(**values):
    environment = os.environ.copy()
    environment.update(
        PYTHON_DOTENV_DISABLED="1",
        APP_ENV="production",
        SECRET_KEY="production-test-secret",
    )
    environment.update(values)
    return environment


class ProductionConfiguration(unittest.TestCase):
    def test_production_enables_secure_session_cookie(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            ca_file = Path(directory) / "aiven-ca.pem"
            ca_file.write_text("test certificate", encoding="utf-8")
            with patch.dict(
                os.environ,
                production_environment(DB_SSL_CA=str(ca_file)),
                clear=True,
            ):
                from app import app

                self.assertTrue(app.config["SESSION_COOKIE_SECURE"])

    def test_database_connection_verifies_ca_and_hostname_in_production(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            ca_file = Path(directory) / "aiven-ca.pem"
            ca_file.write_text("test certificate", encoding="utf-8")
            with patch.dict(
                os.environ,
                {
                    "APP_ENV": "production",
                    "DB_SSL_CA": str(ca_file),
                    "DB_HOST": "mysql.example.aivencloud.com",
                    "DB_PORT": "12345",
                    "DB_USER": "todo_app",
                    "DB_PASSWORD": "test-password",
                    "DB_NAME": "registration",
                },
            ), patch("db.pymysql.connect") as connect:
                get_connection()

        self.assertEqual(connect.call_args.kwargs["ssl_ca"], str(ca_file))
        self.assertTrue(connect.call_args.kwargs["ssl_verify_cert"])
        self.assertTrue(connect.call_args.kwargs["ssl_verify_identity"])

    def test_production_rejects_missing_ca_at_startup(self):
        environment = production_environment()
        environment.pop("DB_SSL_CA", None)
        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaisesRegex(RuntimeError, "requires DB_SSL_CA"):
                get_database_tls_options()

    def test_development_does_not_require_or_enable_database_tls(self):
        with patch.dict(
            os.environ,
            {"APP_ENV": "development", "DB_SSL_CA": ""},
        ):
            self.assertEqual(get_database_tls_options(), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
