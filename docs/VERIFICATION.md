# Verification evidence

8 October 2026; current local completion diff over `6ffea51`.

## Environment and setup

- Windows, Python 3.14.4, MySQL 8.4.11, installed Chrome.
- Created a fresh virtual environment outside the repository and installed `requirements.txt` successfully. Live Python integration checks ran using that fresh environment.
- Prerequisites were already installed. This verifies dependency setup and application/schema behavior, not installation on a completely blank operating system.
- Re-ran the complete schema after inserting disposable fixture rows; both tables became empty. No seed accounts are in the shipped DDL.
- Added `uq_todos_user_title` to the configured existing database after confirming there were no duplicate groups. No accounts/tasks were deleted. Also checked the migration against an existing-table fixture in a disposable database.

## Live MySQL checks: passed

`tests/integration.py` uses Flask's test client with real MySQL, not a mocked database:

- Registration required/mismatch/72-byte checks; persisted bcrypt hash comparison; duplicate email; successful register/login routing and root redirect.
- Same login message for wrong password, unknown email and SQL-injection-shaped email; logout/private-route protection.
- Two independent user sessions: private newest-first lists, forged form user IDs ignored, cross-user edit/status/delete unchanged, and private edit/delete-confirmation selection rejected.
- Add/edit/done/open/delete; same-title reuse by a second user; duplicate add/edit blocked without writes; saving the same title/status succeeds.
- Empty/space-only/201-character and 201-emoji title rejection; 200 emojis saved. Invalid add/edit leaves rows unchanged.
- Missing/incorrect CSRF tokens rejected on all task write routes and logout without mutation.
- Friendly 404 for malformed, zero, negative, out-of-range and 5000-digit IDs.
- Foreign key rejected a task owned by a nonexistent user with MySQL 1452; unique titles rejected duplicate INSERT with 1062.
- Live test databases were removed afterward.

## Simulated failure checks: passed

Mocked database outage and unexpected exception checks returned friendly 503 and 500 pages without exposing exception details. These cases are fixture simulations; the actual MySQL server was not stopped. Reused text/background palette pairs were checked against a 4.5:1 contrast threshold, covering the mechanical detector’s unresolved Jinja stylesheet warning.

## JavaScript checks: passed

The two dependency-free Node checks execute the actual scripts with a small simulated DOM. They cover exact required/mismatch/length messages, invalid submission blocking, first-invalid-field focus, code-point name/title boundaries, UTF-8 password limits, and deletion confirmation/cancellation. They are logic regression checks, not browser substitutes.

## Real Chrome: passed

`tests/browser.py` starts a temporary server on a disposable database and runs `tests/browser.test.js` in isolated browser contexts:

- JavaScript enabled and disabled: register/login/logout, required errors, private lists, CRUD, duplicate title feedback, Unicode bounds, stale/missing CSRF and friendly invalid-ID recovery.
- Separate contexts for Sara/Omar: each sees only their own tasks, may use the same title, and cannot mutate the other's rows.
- JavaScript native delete confirmation was both canceled and accepted. Without JavaScript, inline confirmation was canceled and then submitted.
- Layout assertions at 1366 and 360 px: login, registration errors, empty/populated list, inline editing, a 200-emoji title, friendly 404, CSRF recovery and no-JS deletion confirmation. No horizontal document overflow; visible form/button controls at least 40 px tall.
- No uncaught browser page errors in checked journeys.
- Four submission PNGs show real application pages on disposable demonstration data. Additional inspection captures are local design-review evidence.

## Independent visual review

The Impeccable finish reviewer returned **ship** for the approved code-first campus study folio in Operate mode. It opened and validated eleven final desktop/mobile captures, including editing, errors and no-JavaScript confirmation. No material visual fixes remained. There was no image-comp or catalog-reference comparison because the user chose direct coding; functionality and contrast were established by the separate checks above.

## Limits and final delivery

The tests do not certify every browser, accessibility assistive technology, production hosting configuration or concurrent-load workload. The local session cache is process-local. Email inbox ownership is not verified. Screenshots and SQL constraints do not replace each member's ability to explain the code.

No commit, push, deployment, teammate message or course submission was performed for this request. Both members should inspect the running app and review the final diff and explanations before publishing/submitting.
