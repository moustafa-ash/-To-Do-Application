"""Live MySQL checks in a disposable database; never resets DB_NAME from .env."""
import os
import re
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import bcrypt
from html import unescape
import pymysql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
TEST_DB = "registration_verify_" + uuid.uuid4().hex[:12]
assert re.fullmatch(r"registration_verify_[a-f0-9]{12}", TEST_DB)


def admin_connection():
    return pymysql.connect(host=os.environ["DB_HOST"], port=int(os.environ["DB_PORT"]),
                           user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"],
                           charset="utf8mb4", autocommit=True, cursorclass=pymysql.cursors.DictCursor)


def execute_schema(connection):
    sql = (ROOT / "database/schema.sql").read_text().replace("registration", TEST_DB)
    with connection.cursor() as cursor:
        for statement in sql.split(";"):
            if statement.strip():
                cursor.execute(statement)


class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admin = admin_connection()
        try:
            # Execute twice to prove the complete DDL resets cleanly.
            execute_schema(cls.admin)
            with cls.admin.cursor() as cursor:
                cursor.execute(f"INSERT INTO `{TEST_DB}`.users (email,name,password_hash) VALUES (%s,%s,%s)",
                               ("reset-check@example.com", "Reset fixture", "fixture-only"))
                cursor.execute(f"INSERT INTO `{TEST_DB}`.todos (user_id,title) VALUES (%s,%s)", (cursor.lastrowid, "Reset fixture"))
            execute_schema(cls.admin)
            with cls.admin.cursor() as cursor:
                for table in ("users", "todos"):
                    cursor.execute(f"SELECT COUNT(*) AS n FROM `{TEST_DB}`.{table}")
                    assert cursor.fetchone()["n"] == 0, "Schema must reset to empty tables"
            os.environ["DB_NAME"] = TEST_DB
            os.environ["SECRET_KEY"] = uuid.uuid4().hex
            from app import app
            cls.app = app
            cls.app.config["TESTING"] = True
        except Exception:
            with cls.admin.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS `{TEST_DB}`")
            cls.admin.close()
            raise

    @classmethod
    def tearDownClass(cls):
        with cls.admin.cursor() as cursor:
            cursor.execute(f"DROP DATABASE `{TEST_DB}`")
        cls.admin.close()

    def setUp(self):
        self.a = self.app.test_client()
        self.b = self.app.test_client()
        self.a_email = uuid.uuid4().hex + "@example.com"
        self.b_email = uuid.uuid4().hex + "@example.com"

    def post(self, client, path, data=None, follow=True):
        client.get("/todos" if path.startswith("/todos") or path == "/logout" else path)
        with client.session_transaction() as state:
            token = state["csrf_token"]
        return client.post(path, data={**(data or {}), "csrf_token": token}, follow_redirects=follow)

    def register(self, client, email, name="Demo student"):
        response = self.post(client, "/register", dict(name=name, email=email,
                             password="test-password", confirm_password="test-password"))
        self.assertEqual(response.status_code, 200)
        with client.session_transaction() as state:
            return state["user_id"]

    def rows(self, user_id):
        with self.admin.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{TEST_DB}`.todos WHERE user_id=%s ORDER BY todo_id DESC", (user_id,))
            return cursor.fetchall()

    def test_auth_security_and_routing(self):
        self.assertEqual(self.a.get("/todos").status_code, 302)
        response = self.post(self.a, "/register", {})
        for message in ("Name is required", "Email is required", "Password is required", "Confirm password is required"):
            self.assertIn(message.encode(), response.data)
        response = self.post(self.a, "/register", dict(name="A", email=self.a_email, password="x", confirm_password="y"))
        self.assertIn(b"Passwords do not match", response.data)
        response = self.post(self.a, "/register", dict(name="A", email=self.a_email, password="x"*73, confirm_password="x"*73))
        self.assertIn(b"Password is too long", response.data)
        user_id = self.register(self.a, self.a_email)
        self.assertEqual(self.a.get("/").location, "/todos")
        with self.admin.cursor() as cursor:
            cursor.execute(f"SELECT password_hash FROM `{TEST_DB}`.users WHERE user_id=%s", (user_id,))
            stored = cursor.fetchone()["password_hash"]
        self.assertTrue(stored.startswith("$2b$"))
        self.assertTrue(bcrypt.checkpw(b"test-password", stored.encode()))
        duplicate = self.post(self.b, "/register", dict(name="B", email=self.a_email, password="x", confirm_password="x"))
        self.assertIn(b"Email Already Exists", duplicate.data)
        self.post(self.a, "/logout")
        self.assertEqual(self.a.get("/todos").status_code, 302)
        for email, password in ((self.a_email, "wrong"), ("unknown@example.com", "test-password"), ("' OR '1'='1' --", "x")):
            response = self.post(self.a, "/login", dict(email=email, password=password))
            self.assertIn(b"Invalid email or password", response.data)
            with self.a.session_transaction() as state:
                self.assertNotIn("user_id", state)
        response = self.post(self.a, "/login", dict(email=self.a_email, password="test-password"))
        self.assertIn(b"My to-dos", response.data)
        self.assertEqual(self.a.get("/logout").status_code, 405)

    def test_crud_isolation_duplicates_unicode_and_csrf(self):
        aid = self.register(self.a, self.a_email)
        bid = self.register(self.b, self.b_email)
        self.post(self.a, "/todos", {"title": "First task"})
        first = self.rows(aid)[0]["todo_id"]
        self.post(self.a, "/todos", {"title": "Second task"})
        second = self.rows(aid)[0]["todo_id"]
        page = self.a.get("/todos").data
        self.assertLess(page.index(b"Second task"), page.index(b"First task"))
        self.assertNotIn(b"First task", self.b.get("/todos").data)
        # Form identities never override the authenticated session.
        self.post(self.b, "/todos", {"title": "First task", "user_id": aid})
        self.assertEqual(len(self.rows(aid)), 2)
        self.assertEqual(len(self.rows(bid)), 1)
        for path, data in ((f"/todos/{first}/edit", {"title": "Stolen"}),
                           (f"/todos/{first}/done", {"status": "done"}),
                           (f"/todos/{first}/delete", {})):
            response = self.post(self.b, path, data)
            self.assertIn(b"To-do not found", response.data)
        self.assertEqual(self.b.get(f"/todos?edit={first}").status_code, 404)
        self.assertEqual(self.b.get(f"/todos?delete={first}").status_code, 404)
        self.assertIn(b"Delete this to-do?", self.a.get(f"/todos?delete={first}").data)
        self.assertEqual(len(self.rows(aid)), 2)
        self.assertEqual(self.rows(aid)[1]["title"], "First task")
        self.assertEqual(self.rows(aid)[1]["is_done"], 0)
        for title, message in (("   ", b"Title is required"), ("x"*201, b"Title is too long"), ("😀"*201, b"Title is too long")):
            for path in ("/todos", f"/todos/{first}/edit"):
                response = self.post(self.a, path, {"title": title})
                self.assertEqual(response.status_code, 400)
                self.assertIn(message, response.data)
                self.assertEqual(len(self.rows(aid)), 2)
        for path in ("/todos", f"/todos/{second}/edit"):
            response = self.post(self.a, path, {"title": " First task "})
            self.assertEqual(response.status_code, 400)
            self.assertIn(b"A to-do with this title already exists", response.data)
            self.assertEqual(len(self.rows(aid)), 2)
        self.assertIn(b"To-do updated", self.post(self.a, f"/todos/{first}/edit", {"title": "First task"}).data)
        self.post(self.a, f"/todos/{first}/edit", {"title": "😀"*200})
        self.assertEqual(len(self.rows(aid)[1]["title"]), 200)
        for status, expected in (("done", 1), ("done", 1), ("open", 0)):
            response = self.post(self.a, f"/todos/{first}/done", {"status": status})
            self.assertIn(b"To-do status updated", response.data)
            self.assertEqual(self.rows(aid)[1]["is_done"], expected)
        before = self.rows(aid)
        for path in ("/todos", f"/todos/{first}/edit", f"/todos/{first}/done", f"/todos/{first}/delete", "/logout"):
            for token in (None, "incorrect"):
                data = {"title": "Changed", "status": "done"}
                if token: data["csrf_token"] = token
                response = self.a.post(path, data=data)
                self.assertEqual(response.status_code, 400)
                self.assertIn(b"Please reopen the form", response.data)
                self.assertEqual(self.rows(aid), before)
        for invalid in ("0", "-1", "abc", "2147483648", "9"*5000):
            response = self.a.get("/todos?edit=" + invalid)
            self.assertEqual(response.status_code, 404)
            self.assertIn("isn't available", unescape(response.get_data(as_text=True)))
        self.post(self.a, f"/todos/{first}/delete")
        self.post(self.a, f"/todos/{second}/delete")
        self.assertIn(b"Your list is empty", self.a.get("/todos").data)

    def test_friendly_failure_pages(self):
        with self.a.session_transaction() as state:
            state["user_id"] = 1
            state["name"] = "Failure fixture"
        with patch("todos.get_connection", side_effect=pymysql.OperationalError(2003, "fixture")):
            response = self.a.get("/todos")
            self.assertEqual(response.status_code, 503)
            self.assertIn(b"could not be loaded", response.data)
            self.assertNotIn(b"OperationalError", response.data)
        with patch.dict(self.app.config, {"TESTING": False}):
            with patch("todos._get_user_todos", side_effect=RuntimeError("fixture-only")):
                with self.assertLogs(self.app.logger, level="ERROR"):
                    response = self.a.get("/todos")
            self.assertEqual(response.status_code, 500)
            self.assertIn(b"Something went wrong", response.data)
            self.assertNotIn(b"fixture-only", response.data)

    def test_schema_constraints_and_existing_install_migration(self):
        with self.admin.cursor() as cursor:
            with self.assertRaises(pymysql.IntegrityError) as caught:
                cursor.execute(f"INSERT INTO `{TEST_DB}`.todos (user_id,title) VALUES (%s,%s)", (2147483647, "Missing user"))
            self.assertEqual(caught.exception.args[0], 1452)
            user_id = self.register(self.a, self.a_email)
            cursor.execute(f"INSERT INTO `{TEST_DB}`.todos (user_id,title) VALUES (%s,%s)", (user_id, "Schema task"))
            with self.assertRaises(pymysql.IntegrityError) as caught:
                cursor.execute(f"INSERT INTO `{TEST_DB}`.todos (user_id,title) VALUES (%s,%s)", (user_id, "Schema task"))
            self.assertEqual(caught.exception.args[0], 1062)
            cursor.execute(f"CREATE INDEX migration_fk_user ON `{TEST_DB}`.todos (user_id)")
            cursor.execute(f"ALTER TABLE `{TEST_DB}`.todos DROP INDEX uq_todos_user_title")
            migration = (ROOT / "database/migrations/001_unique_todo_titles.sql").read_text().replace("registration", TEST_DB)
            migration = "\n".join(line for line in migration.splitlines() if not line.lstrip().startswith("--"))
            for statement in migration.split(";"):
                if statement.strip(): cursor.execute(statement)
            cursor.execute(f"SELECT COUNT(*) AS n FROM `{TEST_DB}`.todos WHERE user_id=%s", (user_id,))
            self.assertEqual(cursor.fetchone()["n"], 1)
        self.admin.rollback()


if __name__ == "__main__":
    print("Live tests use an isolated registration_verify_* database, created and removed by this script.")
    unittest.main(verbosity=2)
