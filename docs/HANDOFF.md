# Teammate handoff: accounts and personal to-dos

Updated on 8 October 2026 from base commit `5c05140` plus local integration changes, in `D:\To-Do-Application\-To-Do-Application`. This is a development handoff; no message has been sent to the teammate.

## Ownership and shared files

- Moustafa Mohamed (2304252): accounts/authentication, authentication templates/JS, and initial shared setup.
- Ibrahim Hossam (2304248): personal to-do routes, template and JavaScript.
- Coordinate `app.py`, `db.py`, the schema, shared layout/CSS, dependencies and README before editing. One editor at a time. Both members must commit and explain the whole project.

Follow [README setup instructions](../README.md). Use separate local MySQL credentials and `.env`; the complete schema script deletes all `registration` data.

## What is implemented

- Registration/login/logout use bcrypt, parameterized SQL, server-side identity and session rotation. Successful registration/login redirects to `/todos`; protected home redirects there too.
- `app.py` registers both blueprints and enforces CSRF on POST/PUT/PATCH/DELETE. Authentication and every list write/logout form include tokens.
- `todos.py` now contains the list/add/edit/done/open/delete routes. Every route checks the session identity; list queries filter by it and mutation predicates include it.
- `todos.html` and `todos.js` contain forms, title validation, edit navigation, empty/done states, feedback and deletion confirmation.
- `auth.js` now validates both auth forms and focuses the first invalid field; required/mismatch messages and UTF-8 password limits match server checks. Shared CSS/base layout remain empty; no submission screenshots exist.

## Integration completed

The blueprint registration, all to-do CSRF fields, authentication/list redirects, list logout, and auth browser validation are implemented. Live two-user MySQL integration checks passed; browser auth validation and the Node regression check passed. Temporary test accounts/tasks were removed.

Do not repeat the previous blueprint/CSRF implementation tasks. Remaining work is invalid-ID handling, shared styling, full browser evidence and final setup/submission checks.

## Integration contract

| Boundary | Existing behavior / required next step |
| --- | --- |
| Identity | Authentication sets `session["user_id"]` and `session["name"]`; route code must never take user identity from a form. |
| Private routes | Home uses `auth.login_required`. Existing to-do routes use their own positive-integer session check; keep it on every route. A rewrite solely to use the decorator is unnecessary. |
| Blueprint | Implemented names: module `todos.py`, blueprint `todos`, view `index`, endpoint `todos.index`; GET `/todos`. It is now registered in `app.py`. |
| Writes | POST `/todos`, `/todos/<todo_id>/edit`, `/todos/<todo_id>/done`, `/todos/<todo_id>/delete`. Done/open values use form field `status` with values `done` or `open`. |
| Redirects | Both authentication success paths use `todos.index`; home also redirects to it. |
| CSRF | Every write form needs `<input type="hidden" name="csrf_token" value="{{ csrf_token }}">`. FormData requests must include the same field; the checker does not read JSON. Reload forms after authentication/session changes. |
| Logout | The list now has POST logout with CSRF token. The login-page control remains available too; styling/navigation can be consolidated into the future base layout. |
| Connections | Import `get_connection` from `db`; pass SQL values separately, commit successful writes and close connections. Do not import the Flask app into route modules. |
| Isolation | All list/mutation SQL already uses the session user's ID. Live two-user list/mutation checks passed in this change; retain ownership checks and collect final browser evidence. |

## SQL already used

```sql
SELECT todo_id, title, is_done, created_at
FROM todos WHERE user_id = %s ORDER BY todo_id DESC;
INSERT INTO todos (user_id, title) VALUES (%s, %s);
UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s;
UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s;
DELETE FROM todos WHERE todo_id = %s AND user_id = %s;
```

Values are supplied separately to `cursor.execute`. These statements are present, not future implementation tasks. The schema foreign key is `todos.user_id -> users.user_id` with default actions.

## Next tasks

### Moustafa

1. Review the new `auth.js` and its Node check so you can explain the required-field loop, mismatch handling, UTF-8 byte count, safe error rendering and focus behavior.
2. Verify full browser journeys with JavaScript disabled and stale forms. Optionally preserve safe name/email values after errors, never passwords.
3. Coordinate the shared layout/styling and final authentication evidence.

### Ibrahim

1. Fix the observed default malformed-ID 404 and 5000-digit-ID 500: bound input before conversion and render friendly errors.
2. Verify existing to-do browser title checks, edit navigation and deletion confirmation. Check Unicode limits match server behavior.
3. Keep all newly added CSRF fields and list logout when updating templates.

### Together

- Build shared styling/base layout; check laptop and roughly 360 px widths, done/empty states and all error pages.
- Run registration -> list -> writes -> logout with two real users in separate browsers. Attempts to change another user's ID must leave their rows unchanged.
- Test schema/setup on a disposable lab database; never reset a database whose data should be kept.
- Add four required screenshots and write the four README explanations in your own words. Verify both members' contributions.

## Verification and limits

Current checks: live MySQL through Flask's test client passed for two-user registration/login/logout, list redirects, ownership isolation, CRUD, done/open, duplicate handling, server validation and CSRF rejection. Rendered list and edit forms all included tokens. Temporary accounts/tasks were removed; the schema and existing data were not reset.

Actual browser checks passed for auth required messages, password mismatch, oversized password, and a valid form reaching server-side login validation. The checked-in Node regression check passed for Unicode and UTF-8 limits, focus and submission blocking. It uses a simulated DOM, not a real browser.

Earlier isolated mocked checks and ID failure findings preceded this integration; ID failures remain unresolved. A clean install/full schema reset, foreign-key rejection, complete JavaScript-disabled browser journeys, to-do browser confirmation, responsive styling and submission screenshots remain unverified. Sessions remain in-memory and local to one process.

## Git coordination

See [COMMIT_PLAN.md](COMMIT_PLAN.md) for history and future checkpoints. Save/review your own work before pulling. If local edits block a pull, commit them or stash the specific files and inspect the saved diff before restoring it; do not discard them to make a pull succeed. Resolve conflicts together and do not force-push. The pull screenshot from another clone is not evidence that this checkout has a stash or the same conflict.
