# First implementation commit plan

Prepared on 8 October 2026. No staging, commit, or push was performed by the documentation update.

## Current Git state

The repository already has commit `e5b4dad` (`Initial commit`), containing `.gitignore`. The application files are currently untracked, so this will be the first implementation commit, not the repository's literal first commit. Branch `main` is configured to track `origin/main`; origin points to `https://github.com/moustafa-ash/-To-Do-Application.git`. Remote state has not been refreshed.

`.env` and `.venv` are ignored. The credential fields in `.env.example` were checked as obvious placeholders without printing their values. Review them again before committing.

## Proposed checkpoint

Commit message:

```text
Add Flask bootstrap, registration validation, and lab database schema
```

Include existing work: app/session setup, authentication blueprint and form validation, database helper, two-table DDL, dependency pins, safe environment example, current placeholder files, updated README, and handoff/commit plan.

Do not describe this as completed authentication. It has no persisted registration, login/logout, private list, or to-do application behavior yet. Do not include `.env`, `.venv`, bytecode, local database dumps, or screenshots containing credentials. Git does not track empty directories such as `screenshots/`.

## Checks before staging

1. Save your files and agree which existing changes belong to this checkpoint with Ibrahim. The schema already includes `todos`; do not claim someone else's contribution as your own. Each member still needs their own commits.
2. Open the README and handoff and confirm names, IDs, ownership, and the proposed route/session agreement.
3. From the repository root, inspect:

```powershell
git status --short
git log -3 --oneline
git check-ignore .env .venv
git ls-files -- .env
```

`git check-ignore` should print both ignored paths; `git ls-files -- .env` should print nothing. Review `.env.example` locally for fake values only.

Local syntax, Flask route/validation, session, bcrypt-experiment, and installed-version checks passed during documentation preparation. The database helper's earlier successful live connection was reported by Moustafa. The full DDL reset and a clean-machine install were not run; do not claim those passed.

## Stage a specific list when ready

These are instructions for your reviewed commit, not commands already executed:

```powershell
git add -- .gitignore .env.example README.md docs/HANDOFF.md docs/COMMIT_PLAN.md requirements.txt app.py auth.py db.py todos.py database/schema.sql templates/base.html templates/register.html templates/login.html templates/todos.html static/css/style.css static/js/auth.js static/js/todos.js
git diff --cached --stat
git diff --cached --check
git diff --cached
```

Check the staged content, including DDL and documentation. Ensure it has no real passwords or secret keys. If `--check` reports whitespace problems, fix them and stage those files again before committing.

After you have reviewed the staged checkpoint:

```powershell
git commit -m "Add Flask bootstrap, registration validation, and lab database schema"
git status --short
```

This makes a local checkpoint. It does not publish anything.

## Publish separately when ready

After the local commit and teammate coordination:

```powershell
git pull --ff-only
git push origin main
```

These commands use the network and are not part of the documentation update. If the pull fails because histories diverged, resolve the branch state together before pushing; do not force-push. A teammate cloning before this checkpoint is published will not receive the new files.

## Subsequent small commits

- Moustafa: registration persistence and authenticated session, then login/logout, then browser validation.
- Ibrahim: private to-do list and creation, then editing/done/deletion and validation.
- Coordinate shared layout, integration checks, screenshots, and final README evidence.

Keep each commit explainable and checked. Do not add bonus features before the required lab behavior is complete.
