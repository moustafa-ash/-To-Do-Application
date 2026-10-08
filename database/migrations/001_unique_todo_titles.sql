-- Existing installations only. Run once; this keeps all accounts and tasks.
-- Resolve any existing duplicate titles per user before applying this constraint.
USE registration;
ALTER TABLE todos ADD CONSTRAINT uq_todos_user_title UNIQUE (user_id, title);
