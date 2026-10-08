# Teammate handoff: accounts and personal to-dos

Checkpoint: 8 October 2026. This is a development handoff, not a finished application or a message sent to the teammate.

## Ownership

- Moustafa Mohamed (2304252): accounts/authentication in `auth.py`, register/login templates, authentication JavaScript, and initial shared setup.
- Ibrahim Hossam (2304248): personal to-do routes in `todos.py`, `templates/todos.html`, and `static/js/todos.js`.
- Coordinate before editing `app.py`, `db.py`, `database/schema.sql`, `templates/base.html`, `static/css/style.css`, `requirements.txt`, or `README.md`. One editor at a time.
- Both members review both tables and all code and make their own commits. Confirm actual contributions in the final README rather than assuming who wrote existing SQL.

## What is ready

- Flask starts and serves `/` and `/register`.
- `auth.py` is a registered blueprint with registration GET/POST validation.
- Registration validates required fields, matching passwords, name/email lengths, and bcrypt's 72-byte password limit. It does not save users.
- `db.get_connection()` reads local environment settings and returns a PyMySQL connection with dictionary rows. It does not automatically commit writes. Use parameterized values, commit successful writes, and always close connections.
- Server-side sessions use an in-memory cache; the session round-trip check passed. Sessions currently do not represent real logged-in accounts.
- `database/schema.sql` defines both required tables, with `users` created before `todos`.

Follow [README setup instructions](../README.md). Each teammate needs their own local MySQL database and `.env`. Running the full schema script deletes all data in `registration`.

## Proposed integration agreement: confirm together before implementing

| Boundary | Agreement to use |
| --- | --- |
| Identity | After successful registration/login, Moustafa sets `session["user_id"]` and `session["name"]`. Clear previous session contents when authenticating; logout clears the session. These values are not yet populated by the application. |
| To-do page | Ibrahim exposes GET `/todos`, using a blueprint named `todos` and a view named `index`, so the endpoint is `todos.index`. This is a proposed endpoint, not an existing route. |
| Redirects | Successful registration/login redirects to `url_for("todos.index")` after that endpoint is implemented and registered. Do not wire this redirect to a nonexistent endpoint. |
| Private access | Every to-do route checks the authenticated session. If `user_id` is missing, redirect to login once Moustafa's login route exists. Do not temporarily hard-code a real user's ID. |
| Shared connection | Import `get_connection` from `db`. Do not import the Flask `app` object into either route module; that can create circular imports. |
| Isolation | Get `user_id` from the session, never from browser fields. Filter reads by it and include it in every UPDATE/DELETE predicate. |

Ibrahim can work on the template and route structure before authentication is ready. Integrated private-route tests require Moustafa's real registration/login flow. Artificial session values may be used only in isolated tests, not in application code.

## SQL contract for to-do features

The table has `todo_id`, `user_id`, `title` (200 characters maximum), `is_done` (default 0), and `created_at`. Its foreign key references `users.user_id`; leave foreign-key actions at their defaults.

Use the assignment queries with PyMySQL's `%s` placeholders:

```sql
SELECT todo_id, title, is_done, created_at
FROM todos WHERE user_id = %s ORDER BY todo_id DESC;

INSERT INTO todos (user_id, title) VALUES (%s, %s);

UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s;

UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s;

DELETE FROM todos WHERE todo_id = %s AND user_id = %s;
```

Pass values separately to `cursor.execute(statement, values)`; do not use string formatting, interpolation, or f-strings to insert input into SQL. Every successful POST redirects so refreshing does not repeat a write.

## Next tasks

### Moustafa

1. Hash and insert valid registrations with parameters; handle duplicate email as `Email Already Exists` and database failures without raw error pages.
2. Populate the session and redirect after successful registration once the list endpoint is ready.
3. Implement login using bcrypt comparison. Unknown email and wrong password both show `Invalid email or password`.
4. Implement logout and agree with Ibrahim on the private-route guard.
5. Add browser validation with the exact required-field/mismatch messages; preserve server checks when JavaScript is disabled. Preserve safe form values on errors, never passwords.

### Ibrahim

1. Review and verify `todos` DDL with Moustafa. Do not repeatedly reset a database containing useful test accounts.
2. Build the list template, empty-state message, and visible done state.
3. Add private list/add/edit/done/delete routes using the SQL above and session-owned identity.
4. Validate titles in both browser and server: `Title is required` for empty/space-only titles, `Title is too long` over 200 characters. Accept only valid done/open values and handle malformed IDs without stack traces.
5. Ask for confirmation before deletion, show feedback, and redirect after successful writes.

### Together

- Register the to-do blueprint in `app.py` and agree on shared styling before editing shared files.
- Check unauthenticated access, two different users in separate browsers, and attempts to change another user's to-do by sending its ID. The other user's row must remain unchanged.
- Verify required messages with JavaScript enabled and disabled, duplicate email, unknown-email/wrong-password login, SQL-injection input, bcrypt hashes, and logout.
- Check 360 px layout, collect four required screenshots, and write the four README explanations in your own words.

## Evidence and remaining limits

Fresh local Flask test-client checks passed for routes, registration validation including multibyte byte limits, and session storage. Syntax, installed dependency pins, and the isolated bcrypt comparison also passed. Earlier live MySQL and browser results were reported by Moustafa; see README for their scope.

The complete schema reset, live to-do foreign key, account creation, login/logout, to-do routes, two-user isolation, and responsive styling have not been verified. Memory sessions disappear when Flask restarts and are not shared across server processes.

## Working together in Git

See [COMMIT_PLAN.md](COMMIT_PLAN.md) for the checkpoint's proposed staging list. Commit only your own understood work, coordinate shared-file edits, and pull before starting and before pushing. If Git reports a conflict or a divergent branch, stop and resolve it together rather than force-pushing. Nobody should commit `.env`, `.venv`, or test credentials.
