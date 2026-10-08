# Commit plan

Updated on 8 October 2026 for the authentication checkpoint and browser-validation HTML preparation.

## Earlier published checkpoints

- Initial repository commit: `e5b4dad` (`Initial commit`), containing `.gitignore`.
- First implementation commit: [49c9471](https://github.com/moustafa-ash/-To-Do-Application/commit/49c9471903c9fc7d155dfd4461056e60564bd1e4).
- Commit message: `Add Flask bootstrap, registration validation, and lab database schema`.
- Pushed to `origin/main`; the GitHub branch was verified against the full local commit hash after the push.
- Included 17 files: Flask/session bootstrap, registration form and server validation, database helper, both table definitions, dependency pins, safe environment example, placeholders, README, and the documents in `docs/`.
- `.env` and `.venv` were excluded. The working tree was clean immediately after publication.

GitHub initially rejected the push because the author email was private. The unpublished commit was amended to use the noreply address already present in the published initial commit, then pushed successfully. Repository-local `user.email` now uses that noreply address; global configuration and GitHub privacy settings were not changed.

The first implementation checkpoint did not contain persisted authentication. The later documentation update was published as `15e1402` (`update to docs`). The current revision adds the authentication progress below; to-do behavior is still unfinished.

## Verification attached to the checkpoint

- Local Flask test-client checks passed for home/register routes, required messages, password mismatch, name/email limits, ASCII and multibyte password byte limits, and session storage.
- Python syntax, the isolated bcrypt comparison experiment, and installed dependency pins passed during documentation preparation.
- Documentation links were fixed for the move into `docs/` and checked before publication.
- Python syntax and staged whitespace checks passed after removing trailing blank lines. Staged files were reviewed before committing.
- Earlier live MySQL connection, users-table constraints, and browser results were reported by Moustafa; they were not repeated during publication.

The complete DDL reset, clean-machine setup, live to-do foreign key, account creation, two-user isolation, and final browser journeys were not verified. Do not describe them as passed.

## Authentication checkpoint: this revision

Commit message: `Add account authentication, CSRF protection, and form validation hooks`.

Scope: the tutoring work in `app.py` and `auth.py`; register/login templates; the custom CSRF error page; updated README, handoff, and this plan. Includes registration persistence, bcrypt comparison, session identity/rotation, login/logout, protected home, and global CSRF form checks. The requested HTML preparation loads the empty `auth.js`; JavaScript validation is not implemented.

Fresh local syntax, template/form/token checks, Flask validation, CSRF rejection/acceptance, protected access, session rotation, login/logout, parameterized query handling, duplicate-email and database/hash failure checks passed. Database calls were mocked. Moustafa separately reported the live checks listed in README; no live SQL or reset was run during this revision.

Exact staging scope for this checkpoint:

```powershell
git add -- app.py auth.py templates/register.html templates/login.html templates/csrf_error.html README.md docs/HANDOFF.md docs/COMMIT_PLAN.md
git diff --cached --stat
git diff --cached --check
git diff --cached
```

Review these files and exclude credentials, virtual environments, unrelated changes, and teammate work. The schema is not changed by this checkpoint. Verify the pushed commit on GitHub after publishing; the commit containing this document identifies this revision.

## Next small implementation commits

| Owner | Suggested commit message | Scope and checks |
| --- | --- | --- |
| Moustafa | `Add browser authentication validation` | Implement `auth.js` against the existing form markers/error containers. Check exact messages before submission, safe text rendering, matching passwords and length limits; retain server checks with JavaScript disabled. |
| Moustafa | `Preserve safe authentication form values` | Retain names/emails after errors, never passwords. Check HTML escaping and that sensitive values are not refilled. |
| Ibrahim | `Add private to-do listing and creation` | Register the agreed blueprint, apply `login_required`, use session-owned identity, include CSRF fields, list newest first, validate/add titles and empty state. Check two users, logged-out access, title limits, and foreign-key behavior. |
| Ibrahim | `Add to-do editing, completion, and deletion` | Edit title, done/open state, deletion confirmation, CSRF tokens and user-scoped predicates. Check malformed input and cross-user mutation attempts. |
| Both, one shared-file editor at a time | `Integrate authentication with the to-do layout` | Replace temporary home redirects after the list endpoint exists; move name/logout controls into shared layout and add responsive styling. Check about 360 px and full authentication/list journeys. |
| Both | `Document verified lab setup and submission evidence` | Reconcile R1-R10, verify clean setup and reset only a disposable database, add four screenshots and the four explanations in your own words. Record actual contributors. |

Each teammate must make their own commits and understand both parts. Keep bonus features out until required behavior is complete.

## Routine for each future commit

1. Coordinate shared-file ownership; pull before starting and before pushing.
2. Save and check the actual changed behavior. Keep README evidence accurate.
3. Inspect changes and credential exclusions:

```powershell
git status --short
git diff
git check-ignore .env .venv
git ls-files -- .env
```

The ignored-path check should print `.env` and `.venv`; the tracked-file check for `.env` should print nothing. Keep only fake values in `.env.example`.

4. Stage only the files belonging to the completed change, inspect the staged diff, and pass `git diff --cached --check` before committing with a matching message.
5. Before publishing:

```powershell
git pull --ff-only
git push origin main
```

If histories diverge or conflicts occur, resolve them together before pushing. Do not force-push over teammate work. Confirm GitHub contains the pushed commit.
