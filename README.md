# Login and To-Do Application

This is our project for Database Lab 2 at Alexandria National University. Users can create an account, log in and manage their own to-do list. The database is called `registration`, and all database operations use plain SQL.

## Team

| Name | Student ID | Work |
| --- | --- | --- |
| Moustafa Mohamed | 2304252 | Project setup, accounts and authentication, password hashing, sessions, CSRF protection and shared integration. |
| Ibrahim Hossam | 2304248 | Personal to-do lists, adding/editing/deleting tasks, done/open status, task forms and validation, and handling oversized task IDs. |

Moustafa uses `moustafa-ash` on GitHub and Ibrahim uses `i949`. We both have commits in this repository.

## Technology

- **Back end:** Python and Flask. PyMySQL connects to MySQL, bcrypt hashes passwords, Flask-Session/cachelib handles sessions, and python-dotenv loads `.env`.
- **Front end:** HTML, Jinja templates, CSS and JavaScript.
- **Database:** MySQL, with `users` and `todos` tables.

The project was tested with Python 3.14.4 and MySQL 8.4.11 on Windows. [requirements.txt](requirements.txt) lists the Python packages. Node.js is only needed for the JavaScript tests.

## How to run

Windows PowerShell. Requires Python 3.14, Git, a running MySQL Server and DBeaver.

### 1. Clone the repository

```powershell
git clone https://github.com/moustafa-ash/-To-Do-Application.git
```

### 2. Enter the project folder

```powershell
cd .\-To-Do-Application
```

### 3. Create the virtual environment

```powershell
python -m venv .venv
```

### 4. Install the packages

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 5. Prepare the database in DBeaver

Connect to MySQL using your host, port, username and password. Open the appropriate SQL file, select that connection, then choose **SQL Editor → Execute SQL script**.

**New installation:** run [database/schema.sql](database/schema.sql) once. It creates the complete database, so skip both migrations afterward. **This script deletes any existing `registration` database and all its accounts and tasks. Do not use it to update a database you want to keep.**

**Existing database:** keep your data and back it up first. Check its columns and indexes:

```sql
DESCRIBE registration.todos;
SHOW INDEX FROM registration.todos;
```

| When to use it | SQL file to run once |
| --- | --- |
| `uq_todos_user_title` is missing from `Key_name` | [001_unique_todo_titles.sql](database/migrations/001_unique_todo_titles.sql) |
| `due_date` is missing from the columns | [002_add_todo_due_date.sql](database/migrations/002_add_todo_due_date.sql) |

Before migration 001, check for duplicates and rename any conflicting titles within the same user's list until this query returns no rows:

```sql
SELECT user_id, title, COUNT(*) AS copies
FROM registration.todos
GROUP BY user_id, title
HAVING COUNT(*) > 1;
```

If both changes are missing, run 001 then 002. If both exist, skip both migrations. These migrations preserve accounts and tasks; do not rerun them once applied. The All / Open / Done filters need no migration.

### 6. Create `.env` (new clone only; keep an existing `.env`)

```powershell
Copy-Item .env.example .env
```

### 7. Generate a secret key

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

### 8. Open `.env` and save your MySQL details and generated key

```powershell
notepad .env
```

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=registration
SECRET_KEY=paste_the_generated_key_here
```

### 9. Check the database connection

```powershell
.\.venv\Scripts\python.exe -c "from db import get_connection; connection = get_connection(); print('Connected to MySQL successfully'); connection.close()"
```

### 10. Start Flask

```powershell
.\.venv\Scripts\python.exe -m flask --app app run
```

### 11. Open the registration page

[http://127.0.0.1:5000/register](http://127.0.0.1:5000/register)

## Features

| Requirement | What the app does |
| --- | --- |
| R1 | Register with name, email, password and confirmation. Duplicate email shows `Email Already Exists`. Successful registration logs the user in and opens the list. |
| R2 | Log in with email and password. Wrong password and unknown email both show `Invalid email or password`. Logout clears the session. |
| R3 | Redirect visitors to login. Logged-in users only see their own tasks, newest first. |
| R4 | Add a task with an optional due date. |
| R5 | Edit a task's title and optional due date. |
| R6 | Mark a task done or open. Done tasks have a check mark, a crossed-out title and a `Done` label. |
| R7 | Delete a task after confirmation. With JavaScript disabled, the app shows a confirmation row with Delete and Cancel buttons. |
| R8 | Validate forms in JavaScript and again on the server. Invalid input shows messages on the same page without saving changes. |
| R9 | Store bcrypt password hashes, use SQL parameters, and take the user ID from the server-side session. UPDATE and DELETE also check task ownership. |
| R10 | Use the same styling across pages, support phone-sized screens, and show errors, success messages, an empty-list message, the user's name and logout. Invalid links and failed requests have styled error pages. |

The validation messages match the assignment: `Name is required`, `Email is required`, `Password is required`, `Confirm password is required`, `Passwords do not match`, `Title is required` and `Title is too long`.

Titles can contain up to 200 characters, including emojis. Empty or space-only titles are rejected. Passwords are limited to 72 UTF-8 bytes because of bcrypt. Write forms also include CSRF tokens.

The app prevents duplicate titles in the same user's list. Another user can use the same title. With the fresh schema, capitalization doesn't make a title different, and a done task still keeps its title.

### Bonus

We added **dark mode**, **automated tests**, optional **due dates for tasks**, **All / Open / Done filters**, and an **open-task count**. The assignment caps the bonus at +1.

Use All, Open or Done above the list to choose which tasks to show. All is the default. The filter stays selected when you add, edit, change a task's status or delete it, and filtering also works with JavaScript turned off.

The number beside “Your list” shows how many of your tasks are still open. It updates when you add, complete, reopen or delete a task, and shows the same total whichever filter you choose.

Click the moon in light mode to switch to dark mode, or the sun to switch back. Your browser remembers the choice. With JavaScript disabled, the site stays in light mode. If local storage is blocked, the switch still works on the current page but the choice isn't saved.

## Screenshots

The screenshots use demonstration accounts in a temporary database. The list views show the filters and the open-task count.

### Register page with error messages

![Registration errors](screenshots/01-register-errors-desktop.png)

### Login page

![Login page](screenshots/02-login-desktop.png)

### List with filters, two open tasks and one done

![To-do list with All, Open and Done filters and a count of two open tasks](screenshots/03-todos-desktop.png)

### Phone-sized window, 360 px wide

![Filters and open-task count on a 360 px phone-sized screen](screenshots/04-todos-mobile-360.png)

### Dark mode

![Filters and open-task count in dark mode on a laptop](screenshots/05-todos-dark-desktop.png)

![Filters and open-task count in dark mode on a 360 px phone-sized screen](screenshots/06-todos-dark-mobile-360.png)

## Assignment questions

### (a) Why do UPDATE and DELETE include `AND user_id = ?`? What happens if we remove it?

To make sure the user is editing or deleting their own task. It prevents them from changing other users' tasks even if they know their IDs. Without it, someone could edit or delete another user's task by sending its ID. The user ID comes from the session, not the form. In PyMySQL, the placeholder is `%s` instead of `?`.

### (b) What happens if we insert a task for a user ID that doesn't exist? Which constraint is this?

MySQL rejects it because `user_id` is a foreign key referencing `users.user_id`. A to-do must belong to a user who exists in the users table. This is the referential integrity constraint.

### (c) Why do we store a hash instead of the password?

To avoid exposing users' passwords if the database is leaked. We store a salted bcrypt hash and compare the entered password with that hash during login.

### (d) Why check for an empty name when the column is `NOT NULL`?

`NOT NULL` only checks for null values. An empty string isn't null, so we still need our own check for empty strings. The app also trims spaces before checking the name.

## Tests

The database tests use a temporary `registration_verify_*` database and remove it afterward. Your MySQL account needs permission to create and drop databases for these tests. They don't reset the normal `registration` database.

```powershell
.\.venv\Scripts\python.exe -X utf8 -B tests/integration.py
```

For the JavaScript checks, install Node.js and run:

```powershell
node tests/auth_validation.test.js
node tests/todos_validation.test.js
node tests/theme.test.js
```

The optional browser tests need Node.js, Google Chrome and Playwright:

```powershell
npm install --prefix "$env:TEMP\todo-browser-checks" --no-package-lock playwright
$env:NODE_PATH = "$env:TEMP\todo-browser-checks\node_modules"
.\.venv\Scripts\python.exe -X utf8 -B tests/browser.py
```

These check registration, login/logout, task changes, two-user privacy, validation, CSRF, deletion confirmation, filters, open-task counts, both themes and responsive layouts. The browser runner also refreshes the screenshots. Database tests, JavaScript checks and Chrome checks passed locally on 10 October 2026. Dependency installation was checked in a fresh virtual environment; installing the tools on a completely blank Windows machine wasn't repeated.

GitHub Actions runs the Python, MySQL, JavaScript and Chrome checks on every push and pull request. CI uses a disposable MySQL instance with its own temporary credentials. CI screenshots are temporary artifacts uploaded only when a job fails. The local browser command above still refreshes the screenshots in this repository.

This is a local lab app. Restarting Flask clears the in-memory login sessions. Email input checks the format in the browser, but the app doesn't verify that the user owns the email address.
