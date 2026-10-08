# Teammate handoff

Updated 8 October 2026. Base: published commit `6ffea51`, plus the current local completion changes. No message was sent to the teammate and no new commit/push was performed for this request.

## Ownership

- Moustafa Mohamed (2304252): accounts/authentication, initial setup, shared integration.
- Ibrahim Hossam (2304248): original task routes/template/JavaScript and oversized-ID bounds.
- Shared completion: responsive layout, routing repair, duplicate-title policy, friendly errors, integration checks and submission docs, assisted by Codex. Coordinate edits to shared files and review all code together.

## Current behavior

Both blueprints are registered. Registration/login and authenticated `/` redirect to `/todos`. All write forms, including shared-header logout, carry a CSRF token. The list, edit selection and delete confirmation are private to the session user. Add/edit/done/delete SQL keeps session ownership predicates.

The shared base template and CSS now cover auth/list/CSRF/404/405/500 pages. Done/open states are visible without relying only on color. Titles wrap at 360 px, and task actions move below them. JavaScript displays exact validation messages and focuses invalid fields. Server checks still protect requests made without scripts. Safe name/email values survive auth errors; passwords are never refilled.

Oversized and malformed task IDs return friendly 404 responses. The teammate's bounded ID parser is preserved. Browser title length now counts code points, matching Python, and the HTML input no longer truncates emojis by UTF-16 length.

Duplicate titles are rejected per user on add or edit by a database unique key, with `A to-do with this title already exists`. A different user may reuse the title. Done tasks retain it. The database collation determines equality; the fresh schema is case-insensitive. Unchanged title/status saves succeed through `CLIENT.FOUND_ROWS`.

Deletion uses native confirmation with JavaScript. Without scripts, its link opens an inline confirmation at `/todos?delete=<id>`; GET does not write anything, and the final CSRF-protected POST performs deletion. Cancel returns to the list.

## Keep these boundaries

| Boundary | Contract |
| --- | --- |
| Identity | `session["user_id"]` is authoritative; ignore form user IDs. Do not import `app` into route modules. |
| SQL | Pass values separately to `cursor.execute`; retain `AND user_id = %s` on every task mutation. |
| Sessions | In-memory cachelib, single process; restart clears sessions. Authentication rotates the session ID. |
| CSRF | Include hidden `csrf_token` in every write form. The checker accepts form fields, not JSON. Reopen stale forms. |
| Connections | Commit successful writes, roll back failed ones, and close connections. Matched-row counts include unchanged values. |
| Schema | Full schema resets all `registration` data. Existing installations use the one-time migration, after duplicate review. Never silently remove duplicate rows. |
| Templates | Extend `base.html`; use the existing button/form/state styles. Keep the no-JS delete confirmation and escaped task text. |

## Existing-installation action for Ibrahim

Pull the completion commit after it is published, preserving local edits first. Keep your own `.env`. Check `SHOW INDEX FROM registration.todos` for `uq_todos_user_title`; if absent, follow the README duplicate query and run `database/migrations/001_unique_todo_titles.sql` once. Do not run the full schema if you want to keep existing accounts/tasks.

The migration has already been applied to Moustafa's existing database without deleting rows. Fresh schema users skip it.

## Checked evidence

See [VERIFICATION.md](VERIFICATION.md). Live MySQL checks passed in disposable databases, including two-user isolation, CRUD, duplicate emails/titles, Unicode boundaries, no-op saves, CSRF, FK rejection and populated reset. Real isolated Chrome checks passed with scripts on/off, including deletion confirm/cancel. All major page states were checked at 1366 and 360 px; the four submission screenshots are linked in README.

The README explanations are drafted. Each member must review and explain them independently. Published history has contributions from both members, but this completion diff still needs review, commit and push. Follow [COMMIT_PLAN.md](COMMIT_PLAN.md); do not force-push or discard a teammate's edits to make a pull succeed.

## Remaining human delivery steps

1. Restart your normal Flask server to load Python changes and inspect the application yourselves.
2. Review the four explanations and understand authentication, ownership, constraints, Unicode length and CSRF.
3. Review and publish the completion diff when authorized; confirm the GitHub checkout contains the screenshots and migration.
4. Submit the one repository through the course process. No deployment or external submission was performed.
