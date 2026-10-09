"""Live MySQL checks in a disposable database; never resets DB_NAME from .env."""
import os
import re
import sys
import unittest
import uuid
from html import unescape
from pathlib import Path
from unittest.mock import patch

import bcrypt
import pymysql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")
TEST_DB = "registration_verify_" + uuid.uuid4().hex[:12]
assert re.fullmatch(r"registration_verify_[a-f0-9]{12}", TEST_DB)


def admin_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        charset="utf8mb4",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )


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
                cursor.execute(
                    f"INSERT INTO `{TEST_DB}`.users (email,name,password_hash) VALUES (%s,%s,%s)",
                    ("reset-check@example.com", "Reset fixture", "fixture-only"),
                )
                cursor.execute(
                    f"INSERT INTO `{TEST_DB}`.todos (user_id,title) VALUES (%s,%s)",
                    (cursor.lastrowid, "Reset fixture"),
                )
            execute_schema(cls.admin)
            with cls.admin.cursor() as cursor:
                for table in ("users", "todos"):
                    cursor.execute(f"SELECT COUNT(*) AS n FROM `{TEST_DB}`.{table}")
                    assert cursor.fetchone()["n"] == 0, (
                        "Schema must reset to empty tables"
                    )
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
        return client.post(
            path, data={**(data or {}), "csrf_token": token}, follow_redirects=follow
        )

    def register(self, client, email, name="Demo student"):
        response = self.post(
            client,
            "/register",
            dict(
                name=name,
                email=email,
                password="test-password",
                confirm_password="test-password",
            ),
        )
        self.assertEqual(response.status_code, 200)
        with client.session_transaction() as state:
            return state["user_id"]

    def rows(self, user_id):
        with self.admin.cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM `{TEST_DB}`.todos WHERE user_id=%s ORDER BY todo_id DESC",
                (user_id,),
            )
            return cursor.fetchall()

    def test_filters_privacy_defaults_and_empty_states(self):
        aid = self.register(self.a, self.a_email)
        bid = self.register(self.b, self.b_email)
        for client, uid, prefix in ((self.a, aid, "Mine"), (self.b, bid, "Private")):
            self.post(client, "/todos", {"title": prefix + " open"})
            self.post(client, "/todos", {"title": prefix + " done"})
            self.post(client, f"/todos/{self.rows(uid)[0]['todo_id']}/done", {"status": "done"})
        for client, own, other in ((self.a, "Mine", "Private"), (self.b, "Private", "Mine")):
            for query, expected in (("", "all"), ("?filter=invalid", "all"),
                                    ("?filter=", "all"), ("?filter=done%27%20OR%201=1", "all"),
                                    ("?filter=all", "all"), ("?filter=open", "open"), ("?filter=done", "done")):
                page = client.get("/todos" + query).get_data(as_text=True)
                self.assertIn(f'filter={expected}" aria-current="page"', page)
                self.assertNotIn(other + " open", page)
                self.assertNotIn(other + " done", page)
                for state in ("open", "done"):
                    self.assertEqual(own + " " + state in page, expected in ("all", state))
                if expected == "all":
                    self.assertLess(page.index(own + " done"), page.index(own + " open"))
        for row in self.rows(aid):
            self.post(self.a, f"/todos/{row['todo_id']}/done?filter=open", {"status": "done"})
        self.assertIn(b"No open to-dos", self.a.get("/todos?filter=open").data)
        for row in self.rows(aid):
            self.post(self.a, f"/todos/{row['todo_id']}/done?filter=done", {"status": "open"})
        self.assertIn(b"No done to-dos yet", self.a.get("/todos?filter=done").data)
        for row in self.rows(aid):
            self.post(self.a, f"/todos/{row['todo_id']}/delete")
        for value in ("all", "open", "done"):
            page = self.a.get("/todos?filter=" + value).data
            self.assertIn(b"Your list is empty", page)
            self.assertIn(b"Add a to-do above to get started.", page)

    def test_filters_preserved_through_forms_and_status_changes(self):
        aid = self.register(self.a, self.a_email)
        bid = self.register(self.b, self.b_email)
        self.post(self.b, "/todos", {"title": "Other user's task"})
        private_id = self.rows(bid)[0]["todo_id"]
        for value in ("all", "open", "done"):
            query = "?filter=" + value
            expected_url = "/todos" + (query if value != "all" else "")
            response = self.post(self.a, "/todos" + query, {"title": "Filter task"}, follow=False)
            self.assertEqual(response.location, expected_url)
            todo_id = self.rows(aid)[0]["todo_id"]
            if value == "done":
                self.post(self.a, f"/todos/{todo_id}/done" + query, {"status": "done"})
            self.post(self.a, "/todos" + query, {"title": "Duplicate fixture"})
            for action in ("edit", "delete"):
                page = self.a.get(f"/todos{query}&{action}={todo_id}").get_data(as_text=True)
                self.assertIn(f'href="/todos{query}">Cancel</a>', page)
                self.assertIn(f'action="/todos/{todo_id}/{action}{query}"', page)
                self.assertEqual(self.a.get(f"/todos{query}&{action}={private_id}").status_code, 404)
            for path in ("/todos", f"/todos/{todo_id}/edit"):
                for data in ({"title": " "}, {"title": "x" * 201},
                             {"title": "Filter task", "due_date": "2027-02-29"},
                             {"title": "Duplicate fixture"}):
                    response = self.post(self.a, path + query, data)
                    self.assertEqual(response.status_code, 400)
                    page = response.get_data(as_text=True)
                    self.assertIn(f'filter={value}" aria-current="page"', page)
                    self.assertIn(f'action="{path}{query}"', page)
            response = self.post(self.a, f"/todos/{todo_id}/edit" + query,
                                 {"title": "Renamed task", "due_date": "2028-02-29"}, follow=False)
            self.assertEqual(response.location, expected_url)
            self.assertEqual(next(row for row in self.rows(aid) if row["todo_id"] == todo_id)["due_date"].isoformat(), "2028-02-29")
            response = self.post(self.a, f"/todos/{todo_id}/done" + query,
                                 {"status": "open" if value == "done" else "done"})
            self.assertEqual(response.request.path + ("?" + response.request.query_string.decode() if response.request.query_string else ""), expected_url)
            if value != "all":
                self.assertNotIn(b"Renamed task", response.data)
            for status in ("invalid", "done", "open"):
                response = self.post(self.a, f"/todos/{todo_id}/done" + query, {"status": status}, follow=False)
                self.assertEqual(response.location, expected_url)
            response = self.post(self.a, f"/todos/{todo_id}/delete" + query, follow=False)
            self.assertEqual(response.location, expected_url)
            self.assertFalse(any(row["todo_id"] == todo_id for row in self.rows(aid)))
            for row in self.rows(aid):
                self.post(self.a, f"/todos/{row['todo_id']}/delete")

    def test_auth_security_and_routing(self):
        self.assertEqual(self.a.get("/todos").status_code, 302)
        response = self.post(self.a, "/register", {})
        for message in (
            "Name is required",
            "Email is required",
            "Password is required",
            "Confirm password is required",
        ):
            self.assertIn(message.encode(), response.data)
        response = self.post(
            self.a,
            "/register",
            dict(name="A", email=self.a_email, password="x", confirm_password="y"),
        )
        self.assertIn(b"Passwords do not match", response.data)
        response = self.post(
            self.a,
            "/register",
            dict(
                name="A",
                email=self.a_email,
                password="x" * 73,
                confirm_password="x" * 73,
            ),
        )
        self.assertIn(b"Password is too long", response.data)
        user_id = self.register(self.a, self.a_email)
        self.assertEqual(self.a.get("/").location, "/todos")
        with self.admin.cursor() as cursor:
            cursor.execute(
                f"SELECT password_hash FROM `{TEST_DB}`.users WHERE user_id=%s",
                (user_id,),
            )
            stored = cursor.fetchone()["password_hash"]
        self.assertTrue(stored.startswith("$2b$"))
        self.assertTrue(bcrypt.checkpw(b"test-password", stored.encode()))
        duplicate = self.post(
            self.b,
            "/register",
            dict(name="B", email=self.a_email, password="x", confirm_password="x"),
        )
        self.assertIn(b"Email Already Exists", duplicate.data)
        self.post(self.a, "/logout")
        self.assertEqual(self.a.get("/todos").status_code, 302)
        for email, password in (
            (self.a_email, "wrong"),
            ("unknown@example.com", "test-password"),
            ("' OR '1'='1' --", "x"),
        ):
            response = self.post(self.a, "/login", dict(email=email, password=password))
            self.assertIn(b"Invalid email or password", response.data)
            with self.a.session_transaction() as state:
                self.assertNotIn("user_id", state)
        response = self.post(
            self.a, "/login", dict(email=self.a_email, password="test-password")
        )
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
        for path, data in (
            (f"/todos/{first}/edit", {"title": "Stolen"}),
            (f"/todos/{first}/done", {"status": "done"}),
            (f"/todos/{first}/delete", {}),
        ):
            response = self.post(self.b, path, data)
            self.assertIn(b"To-do not found", response.data)
        self.assertEqual(self.b.get(f"/todos?edit={first}").status_code, 404)
        self.assertEqual(self.b.get(f"/todos?delete={first}").status_code, 404)
        self.assertIn(b"Delete this to-do?", self.a.get(f"/todos?delete={first}").data)
        self.assertEqual(len(self.rows(aid)), 2)
        self.assertEqual(self.rows(aid)[1]["title"], "First task")
        self.assertEqual(self.rows(aid)[1]["is_done"], 0)
        for title, message in (
            ("   ", b"Title is required"),
            ("x" * 201, b"Title is too long"),
            ("😀" * 201, b"Title is too long"),
        ):
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
        self.assertIn(
            b"To-do updated",
            self.post(self.a, f"/todos/{first}/edit", {"title": "First task"}).data,
        )
        self.post(self.a, f"/todos/{first}/edit", {"title": "😀" * 200})
        self.assertEqual(len(self.rows(aid)[1]["title"]), 200)
        for status, expected in (("done", 1), ("done", 1), ("open", 0)):
            response = self.post(self.a, f"/todos/{first}/done", {"status": status})
            self.assertIn(b"To-do status updated", response.data)
            self.assertEqual(self.rows(aid)[1]["is_done"], expected)
        before = self.rows(aid)
        for path in (
            "/todos",
            f"/todos/{first}/edit",
            f"/todos/{first}/done",
            f"/todos/{first}/delete",
            "/logout",
        ):
            for token in (None, "incorrect"):
                data = {"title": "Changed", "status": "done"}
                if token:
                    data["csrf_token"] = token
                response = self.a.post(path, data=data)
                self.assertEqual(response.status_code, 400)
                self.assertIn(b"Please reopen the form", response.data)
                self.assertEqual(self.rows(aid), before)
        for invalid in ("0", "-1", "abc", "2147483648", "9" * 5000):
            response = self.a.get("/todos?edit=" + invalid)
            self.assertEqual(response.status_code, 404)
            self.assertIn("isn't available", unescape(response.get_data(as_text=True)))
        self.post(self.a, f"/todos/{first}/delete")
        self.post(self.a, f"/todos/{second}/delete")
        self.assertIn(b"Your list is empty", self.a.get("/todos").data)

    def test_due_date_validation_editing_and_user_isolation(self):
        aid = self.register(self.a, self.a_email)
        bid = self.register(self.b, self.b_email)

        self.post(self.a, "/todos", {"title": "No due date", "due_date": ""})
        blank_due = next(row for row in self.rows(aid) if row["title"] == "No due date")
        self.assertIsNone(blank_due["due_date"])

        self.post(
            self.a,
            "/todos",
            {"title": "Leap day", "due_date": "2028-02-29"},
        )
        leap = next(row for row in self.rows(aid) if row["title"] == "Leap day")
        leap_id = leap["todo_id"]
        self.assertEqual(leap["due_date"].isoformat(), "2028-02-29")
        edit_page = self.a.get(f"/todos?edit={leap_id}").get_data(as_text=True)
        self.assertIn('value="2028-02-29"', edit_page)

        self.post(
            self.a,
            f"/todos/{leap_id}/edit",
            {"title": "Leap day", "due_date": "9999-12-31"},
        )
        self.assertEqual(
            next(row for row in self.rows(aid) if row["todo_id"] == leap_id)[
                "due_date"
            ].isoformat(),
            "9999-12-31",
        )
        self.post(
            self.a,
            f"/todos/{leap_id}/edit",
            {"title": "Leap day", "due_date": ""},
        )
        self.assertIsNone(
            next(row for row in self.rows(aid) if row["todo_id"] == leap_id)[
                "due_date"
            ]
        )

        self.post(
            self.a,
            "/todos",
            {"title": "Minimum date", "due_date": "1000-01-01"},
        )
        minimum = next(row for row in self.rows(aid) if row["title"] == "Minimum date")
        self.assertEqual(minimum["due_date"].isoformat(), "1000-01-01")

        self.post(
            self.a,
            f"/todos/{leap_id}/edit",
            {"title": "Leap day", "due_date": "2028-02-29"},
        )
        for invalid_date in ("0001-01-01", "2027-02-29", "10000-01-01"):
            response = self.post(
                self.a,
                f"/todos/{leap_id}/edit",
                {"title": "Leap day", "due_date": invalid_date},
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn(b"Enter a valid due date", response.data)
            self.assertEqual(
                next(row for row in self.rows(aid) if row["todo_id"] == leap_id)[
                    "due_date"
                ].isoformat(),
                "2028-02-29",
            )

        response = self.post(
            self.a,
            f"/todos/{leap_id}/edit",
            {"title": "   ", "due_date": "2030-01-01"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Title is required", response.data)
        self.assertEqual(
            next(row for row in self.rows(aid) if row["todo_id"] == leap_id)[
                "due_date"
            ].isoformat(),
            "2028-02-29",
        )

        self.post(
            self.a,
            "/todos",
            {"title": "Existing title", "due_date": "2040-04-05"},
        )
        existing = next(
            row for row in self.rows(aid) if row["title"] == "Existing title"
        )
        self.post(
            self.a,
            f"/todos/{leap_id}/edit",
            {"title": "Existing title", "due_date": "2050-05-06"},
        )
        self.assertEqual(
            next(row for row in self.rows(aid) if row["todo_id"] == leap_id)[
                "due_date"
            ].isoformat(),
            "2028-02-29",
        )
        self.assertEqual(existing["due_date"].isoformat(), "2040-04-05")

        self.post(
            self.b,
            "/todos",
            {"title": "Private date", "due_date": "2035-06-07"},
        )
        private = self.rows(bid)[0]
        self.post(
            self.a,
            f"/todos/{private['todo_id']}/edit",
            {"title": "Changed by another user", "due_date": "2045-08-09"},
        )
        self.assertEqual(self.rows(bid)[0]["due_date"].isoformat(), "2035-06-07")

    def test_due_date_migration_selects_database_and_preserves_rows(self):
        migration_db = "registration_verify_migration_" + uuid.uuid4().hex[:12]
        connection = admin_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE `{migration_db}`")
                cursor.execute(
                    f"CREATE TABLE `{migration_db}`.todos ("
                    "todo_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                    "title VARCHAR(200) NOT NULL) ENGINE=InnoDB"
                )
                cursor.execute(
                    f"INSERT INTO `{migration_db}`.todos (title) VALUES (%s)",
                    ("Existing task",),
                )

            # This connection has no default database; the migration must select one.
            migration = (ROOT / "database/migrations/002_add_todo_due_date.sql")
            sql = migration.read_text().replace("registration", migration_db)
            with connection.cursor() as cursor:
                for statement in sql.split(";"):
                    if statement.strip():
                        cursor.execute(statement)
                cursor.execute(
                    f"SELECT title, due_date FROM `{migration_db}`.todos"
                )
                self.assertEqual(
                    cursor.fetchall(), [{"title": "Existing task", "due_date": None}]
                )
        finally:
            with connection.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS `{migration_db}`")
            connection.close()

    def test_friendly_failure_pages(self):
        with self.a.session_transaction() as state:
            state["user_id"] = 1
            state["name"] = "Failure fixture"
        with patch(
            "todos.get_connection",
            side_effect=pymysql.OperationalError(2003, "fixture"),
        ):
            response = self.a.get("/todos")
            self.assertEqual(response.status_code, 503)
            self.assertIn(b"could not be loaded", response.data)
            self.assertNotIn(b"OperationalError", response.data)
        with patch.dict(self.app.config, {"TESTING": False}):
            with patch(
                "todos._get_user_todos", side_effect=RuntimeError("fixture-only")
            ):
                with self.assertLogs(self.app.logger, level="ERROR"):
                    response = self.a.get("/todos")
            self.assertEqual(response.status_code, 500)
            self.assertIn(b"Something went wrong", response.data)
            self.assertNotIn(b"fixture-only", response.data)

    def test_schema_constraints_and_existing_install_migration(self):
        with self.admin.cursor() as cursor:
            with self.assertRaises(pymysql.IntegrityError) as caught:
                cursor.execute(
                    f"INSERT INTO `{TEST_DB}`.todos (user_id,title) VALUES (%s,%s)",
                    (2147483647, "Missing user"),
                )
            self.assertEqual(caught.exception.args[0], 1452)
            user_id = self.register(self.a, self.a_email)
            cursor.execute(
                f"INSERT INTO `{TEST_DB}`.todos (user_id,title) VALUES (%s,%s)",
                (user_id, "Schema task"),
            )
            with self.assertRaises(pymysql.IntegrityError) as caught:
                cursor.execute(
                    f"INSERT INTO `{TEST_DB}`.todos (user_id,title) VALUES (%s,%s)",
                    (user_id, "Schema task"),
                )
            self.assertEqual(caught.exception.args[0], 1062)
            cursor.execute(
                f"CREATE INDEX migration_fk_user ON `{TEST_DB}`.todos (user_id)"
            )
            cursor.execute(
                f"ALTER TABLE `{TEST_DB}`.todos DROP INDEX uq_todos_user_title"
            )
            migration = (
                (ROOT / "database/migrations/001_unique_todo_titles.sql")
                .read_text()
                .replace("registration", TEST_DB)
            )
            migration = "\n".join(
                line
                for line in migration.splitlines()
                if not line.lstrip().startswith("--")
            )
            for statement in migration.split(";"):
                if statement.strip():
                    cursor.execute(statement)
            cursor.execute(
                f"SELECT COUNT(*) AS n FROM `{TEST_DB}`.todos WHERE user_id=%s",
                (user_id,),
            )
            self.assertEqual(cursor.fetchone()["n"], 1)
        self.admin.rollback()


if __name__ == "__main__":
    print(
        "Live tests use an isolated registration_verify_* database, created and removed by this script."
    )
    unittest.main(verbosity=2)
