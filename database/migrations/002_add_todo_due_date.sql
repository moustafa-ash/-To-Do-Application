USE registration;

ALTER TABLE todos
ADD COLUMN due_date DATE NULL AFTER title;
