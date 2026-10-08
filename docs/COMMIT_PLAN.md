# Commit plan

Updated on 8 October 2026 for local integration changes on base revision `5c05140`.

## Recorded checkpoints

| Commit | Scope |
| --- | --- |
| `e5b4dad` | Initial repository and `.gitignore` |
| [49c9471](https://github.com/moustafa-ash/-To-Do-Application/commit/49c9471903c9fc7d155dfd4461056e60564bd1e4) | Flask/session bootstrap, registration validation, database helper and DDL, placeholders and initial docs |
| `15e1402` | Documentation update and schema spacing |
| [24c9b09](https://github.com/moustafa-ash/-To-Do-Application/commit/24c9b09b5e14b0c67b953a901d7c85a3e9e08f73) | Registration persistence, login/logout, session rotation, protected home, CSRF enforcement and authentication HTML hooks |
| `5c05140` | To-do list/add/edit/done/delete routes, template and JavaScript validation/confirmation |

The local HEAD and cached `origin/main` both point to `5c05140` at audit time. No remote fetch was performed during this documentation-only audit. Earlier pushes of `49c9471` and `24c9b09` were verified against GitHub in this session. Repository-local Git author email uses the existing GitHub noreply address; real `.env` and `.venv` are excluded.

## Local integration work ready for review

The four requested tasks are implemented locally: to-do blueprint registration, all to-do CSRF fields, authentication/list redirects plus list logout, and browser authentication validation. Home now redirects to the list. The existing teammate formatting edit in `todos.py` was preserved.

Suggested implementation message: `Connect to-do routes and add authentication browser validation`.

Review `app.py`, `auth.py`, `templates/todos.html`, `static/js/auth.js`, `tests/auth_validation.test.js`, and all three docs. The existing `todos.py` formatting change is separate; do not stage it automatically with this work. No commit or push was performed for this request.

Checks passed: live MySQL two-user authentication/CRUD/isolation/CSRF and server validation through Flask's test client, actual browser auth validation, Node regression boundaries and JS syntax. Temporary test data was removed. These results do not complete styling, ID-error handling or final delivery evidence.

## Next small commits

| Owner | Suggested message and scope |
| --- | --- |
| Ibrahim | `Handle invalid to-do IDs without raw errors`: bound conversion inputs, friendly errors and malformed/oversized/ownership cases. Verify to-do Unicode/browser behavior too. |
| Both, one editor per shared file | `Add shared responsive layout`: base/CSS, clear feedback/navigation/done states on laptop and about 360 px. |
| Both | `Document verified lab delivery`: full browser JavaScript on/off and confirmation journeys, fresh setup/disposable reset, foreign-key rejection, four screenshots and explanations. |

Do not recreate already connected CRUD/authentication. Safe name/email retention is an optional small improvement, never passwords. Bonus features can wait.

## Commit/pull/push routine

1. Save changes, coordinate shared-file editing, and review Git status before starting or pulling.
2. Pull `main` only after preserving local edits:

```powershell
git status --short
git diff
git pull --ff-only origin main
```

If a pull is blocked by local edits, commit the intended work or stash the specific changed files, then pull and inspect the saved diff before restoring. Restore can cause conflicts. Do not discard edits or force-push to bypass them.

3. Run checks appropriate to the changed behavior and keep documentation evidence accurate.
4. Stage only the actual completed change, then review:

```powershell
git diff --cached --stat
git diff --cached --check
git diff --cached
git check-ignore .env .venv
git ls-files -- .env
```

The ignored-path check should list `.env` and `.venv`; the tracked `.env` check should be empty. Only fake values belong in `.env.example`. Each member must commit their own understood contributions.

5. Commit with a message matching final scope. Refresh remote before pushing; if histories diverge, resolve together without force-pushing. After push, verify GitHub contains the resulting commit.

## Current publication status

This request implements the four selected tasks and updates README/handoff/plan. The changes are local and uncommitted; publication requires a separate commit/push request. Credentials and environment files remain excluded. Review teammate changes separately before staging.
