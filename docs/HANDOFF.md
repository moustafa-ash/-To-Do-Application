# Teammate handoff: accounts and personal to-dos

Checkpoint: 8 October 2026. This is a development handoff, not a finished application or a message sent to the teammate.

## Ownership

- Moustafa Mohamed (2304252): accounts/authentication in `auth.py`, register/login templates, authentication JavaScript, and initial shared setup.
- Ibrahim Hossam (2304248): personal to-do routes in `todos.py`, `templates/todos.html`, and `static/js/todos.js`.
- Coordinate before editing `app.py`, `db.py`, `database/schema.sql`, `templates/base.html`, `static/css/style.css`, `requirements.txt`, or `README.md`. One editor at a time.
- Both members review both tables and all code and make their own commits. Confirm actual contributions in the final README rather than assuming who wrote existing SQL.

## What is ready

- Registration validates input, bcrypt-hashes passwords, inserts with parameters, handles duplicate email, populates the session, rotates its ID, and redirects to protected home.
- Login uses a parameterized lookup and bcrypt comparison. Wrong passwords and unknown emails both show `Invalid email or password`. POST logout clears the session.
- `session["user_id"]` and `session["name"]` now represent the authenticated account.
- `auth.login_required` is implemented and applied to `/`; unauthenticated requests redirect to `auth.login`.
- `app.py` checks CSRF form tokens before every POST/PUT/PATCH/DELETE. All three current forms include the hidden token; failed checks get a custom HTTP 400 page.
- Registration/login templates have `data-auth` markers, an always-present `#form-errors` list, and deferred loading of `static/js/auth.js`. The script is empty; browser validation is next.
- `db.get_connection()` returns dictionary rows. Callers must commit successful writes and close connections; the authentication routes already do this.
- `database/schema.sql` defines both required tables; it deletes all `registration` data when run. Memory sessions disappear on server restart.

Follow [README setup instructions](../README.md). Each teammate needs their own MySQL and `.env`.

## Integration boundary: authentication ready, list endpoint still proposed

| Boundary | Agreement to use |
| --- | --- |
| Identity | Use the existing `session["user_id"]` and `session["name"]`; never accept identity from a form. |
| Private routes | Import `login_required` from `auth`. Put `@login_required` below the route decorator on every to-do route, including writes. The existing guard redirects to `auth.login`. |
| To-do page | Proposed GET `/todos`, blueprint `todos`, view `index`, endpoint `todos.index`. Ibrahim still needs to implement it and confirm this naming. |
| Redirects | Authentication currently redirects to `home`. Once the to-do endpoint exists and is registered, Moustafa changes both success redirects to `url_for("todos.index")`. |
| CSRF | Every to-do POST form needs `<input type="hidden" name="csrf_token" value="{{ csrf_token }}">`. For fetch/FormData, send the same field; a JSON-only body is not supported by the current checker. Reload stale forms after authentication changes or a restart. |
| Connections | Import `get_connection` from `db`; pass SQL values separately, commit successful writes, and close connections. Do not import the Flask `app` object into route modules. |
| Isolation | Filter reads by the session user and include that user in every UPDATE/DELETE predicate. |
| Logout | Use a POST form targeting `url_for('auth.logout')` with a CSRF token. Move the temporary login-page name/logout controls into the shared authenticated layout when ready. |

Ibrahim can now integrate with real authentication. Keep test session values confined to isolated tests, not application code.

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

1. Implement the existing `auth.js` hooks with exact browser validation messages while retaining server checks.
2. Preserve safe name/email fields after validation errors; never refill passwords.
3. With Ibrahim, integrate both success redirects with the real list endpoint and move name/logout controls into the authenticated layout.
4. Complete shared styling and final browser checks, including JavaScript-disabled requests, fresh/stale CSRF forms, and required lab security cases.

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

Fresh local Flask test-client checks passed for template hooks, all CSRF fields, token rejection/acceptance, validation, protected access, session rotation, login/logout, parameterized queries, duplicates, and database/hash failure handling. Database calls were mocked; no live SQL or account creation was performed during this update. Syntax and the static script response also passed.

Moustafa reported live account persistence, duplicate prevention, stored hash comparison, login/logout, private home, and CSRF checks during tutoring. These reports are distinguished from the fresh mocked checks in README.

The complete schema reset, live to-do foreign key, clean-machine installation, two-user to-do isolation, browser validation, and responsive styling remain unverified. The in-memory session store is local to one server process.

## Working together in Git

See [COMMIT_PLAN.md](COMMIT_PLAN.md) for checkpoint history and the next small commits. Commit only your own understood work, coordinate shared-file edits, and pull before starting and before pushing. If Git reports a conflict or a divergent branch, stop and resolve it together rather than force-pushing. Nobody should commit `.env`, `.venv`, or test credentials.
