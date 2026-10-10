from datetime import date

import pymysql
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from db import get_connection

todos = Blueprint("todos", __name__)

MAX_TODO_ID = 2_147_483_647
MIN_MYSQL_DATE = date(1000, 1, 1)
MAX_MYSQL_DATE = date(9999, 12, 31)


def _parse_due_date(raw_value):
    """Return (date, valid); an empty field means no due date."""
    if not raw_value:
        return None, True
    try:
        parsed = date.fromisoformat(raw_value)
    except ValueError:
        return None, False
    if parsed.isoformat() != raw_value or not MIN_MYSQL_DATE <= parsed <= MAX_MYSQL_DATE:
        return None, False
    return parsed, True


def _current_user_id():
    """Return the authenticated session identity, or send the user to login."""
    user_id = session.get("user_id")
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id < 1:
        return None
    return user_id


def _todo_id(raw_id):
    if not raw_id.isascii() or not raw_id.isdecimal():
        abort(404)
    normalized_id = raw_id.lstrip("0") or "0"
    max_id_text = str(MAX_TODO_ID)
    if len(normalized_id) > len(max_id_text) or (
        len(normalized_id) == len(max_id_text) and normalized_id > max_id_text
    ):
        abort(404)

    value = int(normalized_id)
    if value < 1:
        abort(404)
    return value


def _get_user_todos(user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT todo_id, title, due_date, is_done, created_at
                    FROM todos WHERE user_id = %s ORDER BY todo_id DESC""",
                (user_id,),
            )
            return cursor.fetchall()
    finally:
        connection.close()


def _render_list(
    user_id,
    *,
    title="",
    due_date="",
    edit_id=None,
    edit_title=None,
    edit_due_date=None,
    delete_id=None,
    status=200,
):
    try:
        user_todos = _get_user_todos(user_id)
        if delete_id is not None and not any(
            todo["todo_id"] == delete_id for todo in user_todos
        ):
            abort(404)
        if edit_id is not None:
            edited = next(
                (todo for todo in user_todos if todo["todo_id"] == edit_id), None
            )
            if edited is None:
                abort(404)
            if edit_title is None:
                edit_title = edited["title"]
            if edit_due_date is None:
                edit_due_date = (
                    edited["due_date"].isoformat() if edited["due_date"] else ""
                )
    except pymysql.MySQLError:
        user_todos = []
        flash("Your to-do list could not be loaded. Please try again.", "error")
        status = 503
    open_todo_count = sum(not todo["is_done"] for todo in user_todos)
    return render_template(
        "todos.html",
        todos=user_todos,
        open_todo_count=open_todo_count,
        title=title,
        due_date=due_date,
        edit_id=edit_id,
        edit_title=edit_title,
        edit_due_date=edit_due_date,
        delete_id=delete_id,
        name=session.get("name", ""),
    ), status


def _require_user():
    user_id = _current_user_id()
    if user_id is None:
        return None, redirect("/login")
    return user_id, None


@todos.get("/todos")
def index():
    user_id, response = _require_user()
    if response:
        return response
    raw_edit_id = request.args.get("edit")
    edit_id = _todo_id(raw_edit_id) if raw_edit_id is not None else None
    raw_delete_id = request.args.get("delete")
    delete_id = _todo_id(raw_delete_id) if raw_delete_id is not None else None
    return _render_list(user_id, edit_id=edit_id, delete_id=delete_id)


@todos.post("/todos")
def add():
    user_id, response = _require_user()
    if response:
        return response

    title = request.form.get("title", "").strip()
    due_date_text = request.form.get("due_date", "")
    due_date_value, valid_due_date = _parse_due_date(due_date_text)
    if not title:
        flash("Title is required", "error")
        return _render_list(
            user_id,
            title=request.form.get("title", ""),
            due_date=due_date_text,
            status=400,
        )
    if len(title) > 200:
        flash("Title is too long", "error")
        return _render_list(user_id, title=title, due_date=due_date_text, status=400)
    if not valid_due_date:
        flash("Enter a valid due date", "error")
        return _render_list(user_id, title=title, due_date=due_date_text, status=400)

    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO todos (user_id, title, due_date) VALUES (%s, %s, %s)",
                (user_id, title, due_date_value),
            )
        connection.commit()
    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()
        if error.args[0] == 1062:
            flash("A to-do with this title already exists", "error")
            return _render_list(
                user_id, title=title, due_date=due_date_text, status=400
            )
        flash("Your to-do could not be added. Please try again.", "error")
        return redirect(url_for("todos.index"))
    finally:
        if connection:
            connection.close()

    flash("To-do added.", "success")
    return redirect(url_for("todos.index"))


@todos.post("/todos/<todo_id>/edit")
def edit(todo_id):
    user_id, response = _require_user()
    if response:
        return response
    todo_id = _todo_id(todo_id)
    title = request.form.get("title", "").strip()
    due_date_text = request.form.get("due_date", "")
    due_date_value, valid_due_date = _parse_due_date(due_date_text)
    if not title:
        flash("Title is required", "error")
        return _render_list(
            user_id,
            edit_id=todo_id,
            edit_title=request.form.get("title", ""),
            edit_due_date=due_date_text,
            status=400,
        )
    if len(title) > 200:
        flash("Title is too long", "error")
        return _render_list(
            user_id,
            edit_id=todo_id,
            edit_title=title,
            edit_due_date=due_date_text,
            status=400,
        )
    if not valid_due_date:
        flash("Enter a valid due date", "error")
        return _render_list(
            user_id,
            edit_id=todo_id,
            edit_title=title,
            edit_due_date=due_date_text,
            status=400,
        )

    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE todos SET title = %s, due_date = %s "
                "WHERE todo_id = %s AND user_id = %s",
                (title, due_date_value, todo_id, user_id),
            )
            changed = cursor.rowcount
        connection.commit()
    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()
        if error.args[0] == 1062:
            flash("A to-do with this title already exists", "error")
            return _render_list(
                user_id,
                edit_id=todo_id,
                edit_title=title,
                edit_due_date=due_date_text,
                status=400,
            )
        flash("Your to-do could not be updated. Please try again.", "error")
        return redirect(url_for("todos.index"))
    finally:
        if connection:
            connection.close()

    flash(
        "To-do updated." if changed else "To-do not found.",
        "success" if changed else "error",
    )
    return redirect(url_for("todos.index"))


@todos.post("/todos/<todo_id>/done")
def set_done(todo_id):
    user_id, response = _require_user()
    if response:
        return response
    todo_id = _todo_id(todo_id)
    value = request.form.get("status", "")
    valid_statuses = {"done": 1, "open": 0}
    if value not in valid_statuses:
        flash("Choose a valid done or open status.", "error")
        return redirect(url_for("todos.index"))

    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
                (valid_statuses[value], todo_id, user_id),
            )
            changed = cursor.rowcount
        connection.commit()
    except pymysql.MySQLError:
        if connection:
            connection.rollback()
        flash("Your to-do status could not be changed. Please try again.", "error")
        return redirect(url_for("todos.index"))
    finally:
        if connection:
            connection.close()

    flash(
        "To-do status updated." if changed else "To-do not found.",
        "success" if changed else "error",
    )
    return redirect(url_for("todos.index"))


@todos.post("/todos/<todo_id>/delete")
def delete(todo_id):
    user_id, response = _require_user()
    if response:
        return response
    todo_id = _todo_id(todo_id)

    connection = None
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM todos WHERE todo_id = %s AND user_id = %s",
                (todo_id, user_id),
            )
            changed = cursor.rowcount
        connection.commit()
    except pymysql.MySQLError:
        if connection:
            connection.rollback()
        flash("Your to-do could not be deleted. Please try again.", "error")
        return redirect(url_for("todos.index"))
    finally:
        if connection:
            connection.close()

    flash(
        "To-do deleted." if changed else "To-do not found.",
        "success" if changed else "error",
    )
    return redirect(url_for("todos.index"))
