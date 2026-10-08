-- Adds optional due dates without deleting existing tasks.
-- Run once against an existing registration database.
ALTER TABLE todos
ADD COLUMN due_date DATE NULL AFTER title;
