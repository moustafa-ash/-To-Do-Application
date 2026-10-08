# Database Lab 2: Login and To-Do Application

A team project for Introduction to Database Systems at Alexandria National University. This is a development checkpoint, not the completed lab submission.

Repository status: 8 October 2026, base revision `5c05140` plus the local integration/browser-validation changes described below. This review covers `D:\To-Do-Application\-To-Do-Application`; it does not establish the state of a teammate's separate clone.

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
- HTML templates, including authentication, to-do, and CSRF error pages. `todos.js` contains title validation and deletion confirmation; `auth.js` validates registration/login. Shared CSS is still empty.
- python-dotenv for local configuration. Package versions are pinned in `requirements.txt`.

## Current status

| Area | Implemented and checked | Still needed |
| --- | --- | --- |
| Database | Both local tables exist; live authentication and to-do writes worked | Disposable full reset and foreign-key rejection checks |
| R1-R2: accounts | bcrypt, parameterized SQL, duplicate handling, login/logout, rotated authenticated identity; success redirects to `/todos` | Final styled pages and optional safe-field retention |
| R3: private list | To-do blueprint registered; visitor redirects; list query uses session user; home redirects to list | Final browser journeys and submission evidence |
| R4-R7: to-dos | Add/edit/done/open/delete with user-scoped SQL; live CRUD and cross-user mutation rejection passed | Browser deletion-confirmation and edit-flow checks |
| R8: validation | Auth JS required/mismatch/length checks; server checks retained; existing to-do title JS/server validation | Full browser JavaScript-disabled scenarios; to-do Unicode boundary consistency |
| R9: security | bcrypt, parameterized queries, session rotation, global CSRF checks; every list write/logout form has a token | Final lab security evidence and failure scenarios |
| R10: interface | Basic forms, feedback, list name/logout, empty/done text, custom CSRF page | Shared styling, responsive layout and friendly invalid-ID errors |

The previous integration blockers are resolved: `todos` is registered, all to-do write forms include CSRF fields, authentication redirects to `todos.index`, and the list has a CSRF-protected logout button. Protected `/` redirects to `/todos`.

Authentication browser validation uses the existing `data-auth` marker and `#form-errors` list. It prevents invalid submissions, displays messages using `textContent`, focuses the first invalid field, and counts password length in UTF-8 bytes to match bcrypt. Name/email length uses Unicode code points to match the server's length checks. Native `type="email"` still provides browser format checking; the server does not verify inbox ownership.

CSRF checks reject missing or incorrect form tokens before route/database work. Forms in older tabs can become stale after authentication changes or server restart; reopen them. The checker reads form fields, not JSON bodies.

Known issue outside this change: malformed to-do IDs use the default 404 page; a 5000-digit edit ID can produce 500. Shared CSS/base layout also remain empty.

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

Open `http://127.0.0.1:5000/register` to create an account, or `http://127.0.0.1:5000/login` to use one. Successful authentication opens `/todos`. Use its **Log out** button to return to login. Opening `/` while authenticated redirects to the list. Keep the terminal running. Stop with Ctrl+C and restart after Python code changes; this command does not enable automatic reloading.

The session store is in memory. It is suitable for this local, single-process lab checkpoint; restarting Flask clears sessions. It is not a shared session store for multiple server processes. The Flask development server is for local development.

## Files

| Path | Purpose / current state |
| --- | --- |
| `app.py` | Flask/session setup, CSRF injection/check, authentication blueprint, protected home route |
| `auth.py` | Registration, login, logout, and reusable `login_required` decorator |
| `db.py` | Shared `get_connection()` helper; callers must close connections and commit successful writes |
| `todos.py` | Registered session-owned list/add/edit/done/delete routes |
| `database/schema.sql` | Destructive, re-runnable DDL for both tables; no seed data |
| `templates/register.html`, `templates/login.html` | Authentication forms, CSRF fields, error containers, deferred script loading |
| `templates/csrf_error.html` | Friendly missing/invalid-token response |
| `templates/todos.html` | To-do forms, CSRF tokens, logout, name, empty/done states and feedback |
| `templates/base.html` | Empty shared-layout placeholder |
| `static/js/todos.js` | Title validation, deletion confirmation, edit navigation; browser execution not verified |
| `static/js/auth.js` | Registration/login browser validation with exact messages and server-compatible limits |
| `tests/auth_validation.test.js` | Dependency-free Node regression check for validation logic |
| `static/css/style.css` | Empty styling placeholder |
| `screenshots/` | Reserved for submission evidence; no screenshots supplied yet |

## Verification recorded on 8 October 2026

### This integration change

Live local MySQL checks through Flask's test client passed for two temporary users: registration/hash storage, list redirects, home/visitor navigation, logout/login, private list visibility, add/edit/done/open/delete, rejection of another user's edit/status/delete attempts, exact title-validation messages without writes, duplicate email, and unknown/wrong-password login. All rendered list/edit/write/logout forms had CSRF tokens; missing/incorrect tokens were rejected. Temporary accounts and their tasks were removed after checking; no schema reset or existing user-data deletion occurred.

Real browser checks passed for registration required messages, password mismatch, the 73-byte password rejection, login required messages, and a valid login form reaching the server and showing `Invalid email or password`. The blocked cases stayed on the form, with focus on the first invalid field. No browser console errors were observed in those checks. A temporary server on port 5055 was used for these checks.

The checked-in Node regression check passed for blocked/allowed submissions, required/mismatch/limit messages, focus, 100 Unicode code-point names, and 72/73-byte ASCII and multibyte password boundaries. It runs the actual script with a small simulated DOM; it is not a browser test.

### Earlier evidence and unresolved checks

Earlier authentication and isolated to-do mocked checks remain documented in the handoff. The prior missing-blueprint/missing-CSRF findings are now fixed; the invalid-ID error issue remains.

No clean-machine installation, destructive full schema reset, live nonexistent-user foreign-key test, full JavaScript-disabled browser journey, to-do deletion-confirmation browser test, responsive design check or submission screenshots were completed in this change.

## Run the browser-validation regression check

With Node.js available, from the project root:

```powershell
node tests/auth_validation.test.js
```

Node is needed only for this development check, not to run the Flask application. No npm packages are required.

## Remaining work, in order

| Priority | Owner | Task / completion check |
| --- | --- | --- |
| 1 | Ibrahim | Bound to-do IDs before conversion, provide friendly malformed/oversized-ID responses, and check to-do browser/server Unicode boundaries. |
| 2 | Both, one editor at a time | Implement shared base layout/CSS. Check all pages on laptop and about 360 px, including feedback, empty/done states and error pages. |
| 3 | Both | Verify full browser journeys, deletion confirmation/edit navigation, JavaScript on/off, stale tokens and remaining lab security cases. |
| 4 | Both | Verify fresh setup and full reset on a disposable database; test foreign-key rejection; gather four screenshots and the four README explanations. |
| 5 | Both | Review actual contributions, reconcile R1-R10 and commit/publish the completed work when authorized. |

Safe name/email retention after server errors is a useful optional form improvement; never refill passwords. Bonus features can wait.

## Before submission

- Complete R1-R10 and run the assignment's security and validation scenarios.
- Confirm that the DDL resets correctly on a disposable lab database.
- Both teammates must make commits and be able to explain the whole project.
- Add at least four screenshots: register errors, login, a populated list with one done item, and a phone-width page (about 360 px).
- Write the README answers in the team's own words after testing: why UPDATE/DELETE need the session user's ID; what a nonexistent foreign-key user causes; why passwords are hashed; why NOT NULL does not reject empty names.
- Keep credentials out of Git and screenshots. Publish only after reviewing the staged files.

The screenshot evidence and four explanatory answers are not complete yet. Bonus features are outside this checkpoint.
