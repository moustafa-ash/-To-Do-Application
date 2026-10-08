# Database Lab 2: Login and To-Do Application

A team project for Introduction to Database Systems at Alexandria National University. This is a development checkpoint, not the completed lab submission.

## Team and ownership

| Member | ID | Responsibility |
| --- | --- | --- |
| Moustafa Mohamed | 2304252 | Accounts, authentication, and initial shared setup |
| Ibrahim Hossam | 2304248 | Personal to-do features |

Shared files have one editor at a time. Both teammates must make commits and understand both tables and all application code. See [the teammate handoff](docs/HANDOFF.md) and [the first implementation commit plan](docs/COMMIT_PLAN.md).

## Technology

- Python and Flask; the current environment uses Python 3.14.4.
- MySQL with PyMySQL and plain SQL; no ORM.
- Flask-Session with cachelib for server-side sessions.
- bcrypt installed for password hashing; not yet connected to registration.
- HTML templates. CSS and JavaScript files currently contain no implementation.
- python-dotenv for local configuration. Package versions are pinned in `requirements.txt`.

## Current status

| Area | Implemented now | Still needed |
| --- | --- | --- |
| Database | DDL for `users` and `todos`, including the foreign key; connection helper returns dictionary rows | Verify the complete reset script and the live `todos` constraints |
| R1: registration | Four-field form, GET/POST route, server-side validation | Hash and insert accounts, handle duplicate email, create the authenticated session, redirect to the list |
| R2: login/logout | Nothing yet | Login, shared error message, logout |
| R3: private list | Session storage configured | Authentication guard and per-user list |
| R4-R7: to-dos | Table definition only | Add, edit, mark done/open, delete with confirmation |
| R8: validation | Registration required fields, matching passwords, column-length limits, bcrypt's 72-byte password limit | JavaScript checks with exact lab messages; to-do validation; retain safe form values on errors |
| R9: security | Credentials loaded from `.env`; server-side session configuration | Application bcrypt hashing/checking and parameterized queries with session-owned `user_id` |
| R10: interface | Basic labeled registration form and error list | Shared styling, responsive layout, empty/done states, logged-in name and logout |

`/` currently displays `To-Do application is running`. `/register` displays and validates a form. Even a valid registration currently just redisplays the page: **it does not create an account**. `/login` and `/todos` do not exist yet.

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

The checkpoint files must be committed and pushed before a teammate can obtain them through this clone command. If the repository is already open in VS Code, use its terminal from the project root instead.

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

Open `http://127.0.0.1:5000/` and `http://127.0.0.1:5000/register`. Keep the terminal running. Stop with Ctrl+C and restart after Python code changes; this command does not enable automatic reloading.

The session store is in memory. It is suitable for this local, single-process lab checkpoint; restarting Flask clears sessions. It is not a shared session store for multiple server processes. The Flask development server is for local development.

## Files

| Path | Purpose / current state |
| --- | --- |
| `app.py` | Flask configuration, session setup, authentication blueprint registration, home route |
| `auth.py` | Authentication blueprint; currently registration validation only |
| `db.py` | Shared `get_connection()` helper; callers must close connections and commit successful writes |
| `todos.py` | Empty placeholder for Ibrahim's routes |
| `database/schema.sql` | Destructive, re-runnable DDL for both tables; no seed data |
| `templates/register.html` | Basic registration form and server error list |
| `templates/base.html`, `login.html`, `todos.html` | Empty placeholders |
| `static/css/style.css`, `static/js/auth.js`, `static/js/todos.js` | Empty placeholders |
| `screenshots/` | Reserved for submission evidence; no screenshots supplied yet |

## Verification recorded on 8 October 2026

Local checks run during documentation preparation passed: Python source compilation without generating bytecode; GET `/` and GET `/register`; POST registration required-field messages, password mismatch, name/email length limits, ASCII and multibyte password byte limits; a server-side session write/read through Flask's test client; an isolated bcrypt correct/wrong-password experiment; installed versions matching `requirements.txt`.

These checks use Flask's test client, not a browser. They do not exercise account creation or to-do behavior. No automated test suite has been added to the repository.

Moustafa reported successful local browser checks of the home/registration pages and validation, a live Python/MySQL connection through `get_connection()`, and database checks of the `users` table: generated ID/timestamp, duplicate email error 1062, and test-row deletion. These earlier results were not re-run against MySQL during this documentation update.

The full reset script, live `todos` foreign-key behavior, installation on an empty machine, JavaScript-disabled browser checks, responsive design, and complete two-user journeys remain unverified.

## Before submission

- Complete R1-R10 and run the assignment's security and validation scenarios.
- Confirm that the DDL resets correctly on a disposable lab database.
- Both teammates must make commits and be able to explain the whole project.
- Add at least four screenshots: register errors, login, a populated list with one done item, and a phone-width page (about 360 px).
- Write the README answers in the team's own words after testing: why UPDATE/DELETE need the session user's ID; what a nonexistent foreign-key user causes; why passwords are hashed; why NOT NULL does not reject empty names.
- Keep credentials out of Git and screenshots. Publish only after reviewing the staged files.

The screenshot evidence and four explanatory answers are not complete yet. Bonus features are outside this checkpoint.
