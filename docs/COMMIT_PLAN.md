# Commit plan

Updated on 8 October 2026 after publishing the first implementation checkpoint.

## Published checkpoint

- Initial repository commit: `e5b4dad` (`Initial commit`), containing `.gitignore`.
- First implementation commit: [49c9471](https://github.com/moustafa-ash/-To-Do-Application/commit/49c9471903c9fc7d155dfd4461056e60564bd1e4).
- Commit message: `Add Flask bootstrap, registration validation, and lab database schema`.
- Pushed to `origin/main`; the GitHub branch was verified against the full local commit hash after the push.
- Included 17 files: Flask/session bootstrap, registration form and server validation, database helper, both table definitions, dependency pins, safe environment example, placeholders, README, and the documents in `docs/`.
- `.env` and `.venv` were excluded. The working tree was clean immediately after publication.

GitHub initially rejected the push because the author email was private. The unpublished commit was amended to use the noreply address already present in the published initial commit, then pushed successfully. Repository-local `user.email` now uses that noreply address; global configuration and GitHub privacy settings were not changed.

This checkpoint does not implement persisted registration, login/logout, a private list, or to-do application behavior. Authentication remains unfinished.

## Verification attached to the checkpoint

- Local Flask test-client checks passed for home/register routes, required messages, password mismatch, name/email limits, ASCII and multibyte password byte limits, and session storage.
- Python syntax, the isolated bcrypt comparison experiment, and installed dependency pins passed during documentation preparation.
- Documentation links were fixed for the move into `docs/` and checked before publication.
- Python syntax and staged whitespace checks passed after removing trailing blank lines. Staged files were reviewed before committing.
- Earlier live MySQL connection, users-table constraints, and browser results were reported by Moustafa; they were not repeated during publication.

The complete DDL reset, clean-machine setup, live to-do foreign key, account creation, two-user isolation, and final browser journeys were not verified. Do not describe them as passed.

## Next small implementation commits

| Owner | Suggested commit message | Scope and checks |
| --- | --- | --- |
| Moustafa | `Add registration persistence and authenticated sessions` | Parameterized INSERT, bcrypt hash, duplicate-email message, transaction/connection handling, authenticated identity, and POST redirect. Check successful registration, duplicate email, stored hash, invalid input without a write, and database failure handling. Agree on an existing redirect endpoint before wiring it. |
| Moustafa | `Add login and logout` | Parameterized lookup, bcrypt comparison, shared `Invalid email or password` message, session lifecycle, and private-route agreement. Check correct/wrong passwords, unknown email, injection input, logout, and unauthenticated access. |
| Ibrahim | `Add private to-do listing and creation` | Register the agreed blueprint, show only the session user's rows newest first, add titles with validation, and show an empty state. Check two users, logged-out access, title boundaries, and foreign-key behavior. Integrated checks depend on real authentication. |
| Ibrahim | `Add to-do editing, completion, and deletion` | Edit title, mark done/open, confirm deletion, and include the session user in every mutation predicate. Check malformed input and attempts to change another user's rows. |
| Both, with one shared-file editor at a time | `Add browser validation and shared responsive layout` | Exact lab messages in the browser while retaining server checks; shared styling, feedback, name/logout controls, empty/done states. Check JavaScript on/off and about 360 px width. |
| Both | `Document verified lab setup and submission evidence` | Reconcile R1-R10, verify setup on a fresh environment and reset only a disposable lab database, add four screenshots and the four explanations in your own words. Record actual contributors. |

These are proposed checkpoints, not completed work or rigid schedules. Each teammate must make their own commits and understand both parts of the application. Keep bonus features out until required behavior is complete.

## Routine for each future commit

1. Coordinate shared-file ownership and save the intended changes. Pull before starting; pull again before pushing.
2. Run checks for the behavior changed. Keep current README claims accurate.
3. Inspect Git and credentials from the repository root:

```powershell
git status --short
git diff
git check-ignore .env .venv
git ls-files -- .env
```

The ignored-path check should print `.env` and `.venv`; the tracked-file check for `.env` should print nothing. Keep only fake values in `.env.example`. Do not include credentials, bytecode, local dumps, or unrelated work.

4. Stage only files belonging to that commit. For example, if a registration change touches only these two files:

```powershell
git add -- auth.py templates/register.html
git diff --cached --stat
git diff --cached --check
git diff --cached
```

Include other files only if that change actually needs them. Fix reported whitespace issues and restage. Review the content before committing.

5. Commit with the message matching the actual completed scope, then review `git status --short`. A local commit does not publish the work.
6. When ready to publish:

```powershell
git pull --ff-only
git push origin main
```

If a pull reports divergent history or a conflict, resolve it together before pushing. Do not force-push over teammate work. Verify that the pushed commit is on GitHub.

## This plan update

This document records the completed publication and replaces the original first-commit instructions. Editing it does not create another commit or push.

If publishing just this documentation update later, its scope is `docs/COMMIT_PLAN.md` and a suitable message is `Update commit plan after publishing initial checkpoint`.
