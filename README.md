# Database Lab 2: Login and To-Do Application

A team project for Introduction to Database Systems at Alexandria National University. This is a development checkpoint, not the completed lab submission.

## Team and ownership

| Member | ID | Responsibility |
| --- | --- | --- |
| Moustafa Mohamed | 2304252 | Accounts, authentication, and initial shared setup |
| Ibrahim Hossam | 2304248 | Personal to-do features |

Shared files have one editor at a time. Both teammates must make commits and understand both tables and all application code. See [the teammate handoff](docs/HANDOFF.md) and [the commit plan](docs/COMMIT_PLAN.md).

## Technology

- Python and Flask; the current environment uses Python 3.14.4.
- MySQL with PyMySQL and plain SQL; no ORM.
- Flask-Session with cachelib for server-side sessions.
- bcrypt for registration hashing and login password comparison.
- HTML templates, including a CSRF error page. Authentication pages load `auth.js`, but that file is still empty; CSS and JavaScript validation are not implemented.
- python-dotenv for local configuration. Package versions are pinned in `requirements.txt`.

## Current status

| Area | Implemented now | Still needed |
| --- | --- | --- |
| Database | DDL for `users` and `todos`, including the foreign key; connection helper returns dictionary rows | Verify the complete reset script and the live `todos` constraints |
| R1: registration | Server validation, bcrypt hash, parameterized INSERT, duplicate-email handling, authenticated session, POST redirect | Replace the temporary home redirect with the real list endpoint when ready |
| R2: login/logout | Parameterized lookup, bcrypt comparison, shared invalid-credentials message, POST logout | Final UI and integration with the list page |
| R3: private list | Reusable `login_required` guard; home route is protected | Apply guard to every to-do route and implement the per-user list |
| R4-R7: to-dos | Table definition only | Add, edit, mark done/open, delete with confirmation |
| R8: validation | Registration/login server checks; registration mismatch and length limits; HTML hooks for browser validation | Implement `auth.js`, to-do validation, and retention of safe form values on errors |
| R9: security | bcrypt, parameterized authentication queries, server-side identity, rotated session ID, CSRF tokens/checks, friendly failure messages | Session-owned `user_id` in every to-do query; CSRF token in every future write form |
| R10: interface | Basic labeled register/login forms, persistent error lists, CSRF error page; temporary name/logout controls on login page | Shared styling, responsive layout, empty/done states, move name/logout controls to the list |

`/register` now creates accounts and logs them in; `/login` authenticates existing accounts. Both redirect to `/`, which shows `To-Do application is running` only for authenticated users and otherwise redirects to login. POST `/logout` clears the session and redirects to login. The logout control is temporarily displayed on `/login` when already logged in. `/todos` does not exist yet.

Registration and login forms have `data-auth` markers and an always-present `#form-errors` list. Both load the empty `static/js/auth.js` with `defer`. These are preparation for browser validation, not working JavaScript validation.

Every POST/PUT/PATCH/DELETE is checked for a session-bound CSRF form token before the route runs. A missing or invalid token returns a custom page with HTTP 400. Load a current form before submitting; login, registration, logout, or a server restart can invalidate tokens in older tabs. Future write forms must include the hidden `csrf_token` field.

The browser's `type="email"` checks basic syntax. The server currently checks that email is present and within the database length limit; it does not verify inbox ownership.

## Setup guide: Windows / PowerShell

These instructions start the current checkpoint. Completing setup does not supply the unfinished application features.

### 1. Install prerequisites and get the project

Install Python (the checked version is 3.14.4), MySQL Server, Git, and DBeaver Community. VS Code is the editor used by the team. Start MySQL Server and have a working local MySQL username and password; DBeaver alone is a client, not the server.

For a new checkout, open PowerShell in your chosen parent folder:

```powershell
git clone https://github.com/moustafa-ash/-To-Do-Application.git
cd .\-To-Do-Application
```

If the repository is already open in VS Code, use its terminal from the project root instead. Existing teammates should pull the published changes before starting work.

### 2. Create the Python environment

On a fresh checkout:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If `.venv` already exists, use it rather than recreating it. All commands below explicitly use its Python executable; activating the environment is optional.

### 3. Build the database in DBeaver

**Warning: `database/schema.sql` starts with `DROP DATABASE IF EXISTS registration;`. Running the full script deletes that database, including all existing accounts and to-dos, and recreates it empty. Use it only for an initial setup or an intentional reset of the lab database.**

1. In DBeaver, create or open a MySQL connection to `localhost`, port `3306`, using your local credentials.
2. Open `database/schema.sql` with **File -> Open File** (or Ctrl+O).
3. If the editor tab shows `<none>`, choose the `localhost` connection through **SQL Editor -> Context** and its connection option. Menu wording can vary by DBeaver version.
4. With no partial text selected, use **SQL Editor -> Execute SQL script** to run all statements. Ctrl+Enter normally runs only the current statement, so it is not the full-script setup step.
5. Confirm that each statement succeeded. In a separate SQL editor connected to localhost, run these individually:

```sql
SHOW TABLES FROM registration;
DESCRIBE registration.users;
DESCRIBE registration.todos;
SHOW CREATE TABLE registration.todos;
```

Expect both tables and a foreign key from `todos.user_id` to `users.user_id`. The schema contains definitions only, not test users or passwords. Keep practice INSERT/DELETE queries in a separate editor.

### 4. Configure local credentials

If `.env` does not exist, create it:

```powershell
Copy-Item .env.example .env
```

Do not overwrite an existing configured `.env`. Edit it locally:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=registration
SECRET_KEY=your_generated_secret_key
```

Generate a secret key with:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Put the generated value in `.env`. Each teammate uses their own credentials and secret key. Never share or commit `.env`; `.env.example` must retain fake values. Restart Flask after changing configuration.

### 5. Check the database helper

```powershell
.\.venv\Scripts\python.exe -c "from db import get_connection; connection = get_connection(); print('Database helper works'); connection.close()"
```

This checks connection settings without changing database data. If it fails, check the running MySQL service, credentials, and whether `registration` exists. Redact credentials before sharing errors.

### 6. Start Flask

```powershell
.\.venv\Scripts\python.exe -m flask --app app run
```

Open `http://127.0.0.1:5000/register` to create an account, or `http://127.0.0.1:5000/login` to use one. Successful authentication opens the protected home page. Visit `/login` while logged in to use the temporary logout button. Keep the terminal running. Stop with Ctrl+C and restart after Python code changes; this command does not enable automatic reloading.

The session store is in memory. It is suitable for this local, single-process lab checkpoint; restarting Flask clears sessions. It is not a shared session store for multiple server processes. The Flask development server is for local development.

## Files

| Path | Purpose / current state |
| --- | --- |
| `app.py` | Flask/session setup, CSRF injection/check, authentication blueprint, protected home route |
| `auth.py` | Registration, login, logout, and reusable `login_required` decorator |
| `db.py` | Shared `get_connection()` helper; callers must close connections and commit successful writes |
| `todos.py` | Empty placeholder for Ibrahim's routes |
| `database/schema.sql` | Destructive, re-runnable DDL for both tables; no seed data |
| `templates/register.html`, `templates/login.html` | Authentication forms, CSRF fields, error containers, deferred script loading |
| `templates/csrf_error.html` | Friendly missing/invalid-token response |
| `templates/base.html`, `templates/todos.html` | Empty placeholders |
| `static/css/style.css`, `static/js/auth.js`, `static/js/todos.js` | Empty placeholders |
| `screenshots/` | Reserved for submission evidence; no screenshots supplied yet |

## Verification recorded on 8 October 2026

Fresh local checks for this authentication checkpoint passed: Python syntax; rendered registration/login/logout CSRF fields; form markers, persistent error containers, and deferred script loading; static `auth.js` response; registration/login required fields and password/length limits; missing, incorrect, and non-ASCII CSRF token rejection; accepted tokens reaching validation; protected home access; authenticated session identity/rotation and logout; duplicate-email handling; parameterized registration/login queries; wrong/unknown/oversized login passwords; malformed stored hashes; and friendly database-failure responses.

These checks used Flask's test client. Authentication database calls were mocked: the checks verified application behavior and generated hash comparison, not a live MySQL journey. No persistent automated test suite has been added to the repository. The JavaScript file was verified as empty, so browser validation remains unfinished.

Moustafa reported successful live checks during tutoring: Python/MySQL connection; users-table ID/timestamp and duplicate constraints; temporary-row deletion; registration persistence with a bcrypt hash; duplicate registration leaving one account; comparison of the stored hash against the correct password; empty/correct/wrong/unknown-email login cases; logged-in identity and logout; private home access; and rejection/acceptance of CSRF submissions. These reported live results were not repeated against MySQL during this update.

The full reset script, live `todos` foreign-key behavior, installation on an empty machine, browser validation with JavaScript on/off, responsive design, and complete two-user to-do journeys remain unverified.

## Before submission

- Complete R1-R10 and run the assignment's security and validation scenarios.
- Confirm that the DDL resets correctly on a disposable lab database.
- Both teammates must make commits and be able to explain the whole project.
- Add at least four screenshots: register errors, login, a populated list with one done item, and a phone-width page (about 360 px).
- Write the README answers in the team's own words after testing: why UPDATE/DELETE need the session user's ID; what a nonexistent foreign-key user causes; why passwords are hashed; why NOT NULL does not reject empty names.
- Keep credentials out of Git and screenshots. Publish only after reviewing the staged files.

The screenshot evidence and four explanatory answers are not complete yet. Bonus features are outside this checkpoint.
