# Commit plan

Updated 8 October 2026. The previously published changes end at `6ffea51`. The new completion work is local and uncommitted; this request did not authorize a new commit or push.

## Recorded history

| Commit | Contributor / scope |
| --- | --- |
| `e5b4dad` | Moustafa: initial repository and ignore rules |
| `49c9471` | Moustafa: bootstrap, registration validation, helper/schema and docs |
| `15e1402` | Moustafa: documentation update |
| `24c9b09` | Moustafa: authentication persistence, login/logout, sessions and CSRF |
| `5c05140` | Ibrahim (`i949`): personal task CRUD, HTML and browser behavior |
| `e20288f` | Ibrahim (`i949`): oversized task ID bounds |
| `6ffea51` | Moustafa: authentication browser validation, task CSRF fields and documentation |

## Completion work ready for review

The current diff restores missing route registration/home navigation, adds the approved shared responsive UI and friendly errors, aligns Unicode title limits, prevents duplicate titles per user, handles unchanged saves, and provides no-JS deletion confirmation. It also contains a one-time existing-database migration, repeatable tests, four real-browser screenshots, README answers/setup and refreshed handoff documentation.

Suggested commit message: `Complete responsive task app and verify lab delivery`.

Review `app.py`, `db.py`, `todos.py`, schema/migration, templates/CSS/JS, tests, screenshots, README/docs and the product/design context. These changes form one reviewed completion checkpoint. Do not invent contributor commits or split the same generated work between identities merely to change attribution; both members already have genuine published contributions.

## Before committing

```powershell
git status --short
git diff --check
git diff
.\.venv\Scripts\python.exe -X utf8 -B tests/integration.py
node tests/auth_validation.test.js
node tests/todos_validation.test.js
git check-ignore .env .venv
git ls-files -- .env
```

The tracked `.env` result must be empty. Review screenshot content and do not include local chooser/review caches. Live tests use disposable databases. Real-browser checks and their optional dependency setup are documented in README.

When commit/push is authorized, stage only the reviewed completion files, inspect `git diff --cached --check` and `git diff --cached`, then commit. Refresh the remote before pushing; preserve local work and resolve any divergence normally. Never force-push over a teammate's history.

## Pulling safely

With a clean working tree:

```powershell
git pull --ff-only origin main
```

If local edits block pulling, commit intended work or stash the specific files first. Inspect the saved diff before restoring it; restoring can cause conflicts. Do not discard edits to bypass the error. After pulling, check both blueprint registrations and run integration tests so a merge cannot silently leave the list disconnected.

## Delivery gates

Both members review and explain the final code/README answers; publish the validated completion commit after authorization; verify GitHub has all four screenshots and DDL; then hand in the repository through the course's process. No GitHub publication or course submission occurred in this completion request.
