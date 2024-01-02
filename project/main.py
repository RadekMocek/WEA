"""Endpointy pro CRUD uživatelových úkolů."""

from datetime import datetime
from typing import Optional

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import Task

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Úvodní stránka."""
    return render_template("index.html")


@main.route("/get_tasks_json")
def get_tasks_json():
    """
    Úkoly ve formátu JSON.

    user_id: Budou vráceny pouze úkoly uživatele s tímto user_id; pokud None, vrací všechny záznamy
    done_filter: Pro =0 vrací vše; pro >0 vrací splněné; pro <0 vrací nesplněné úkoly
    """
    user_id = request.args.get("user_id", default=None, type=int)
    done_filter = request.args.get("done_filter", default=0, type=int)
    tasks_query = Task.query
    if user_id:
        tasks_query = tasks_query.filter_by(user_id=user_id)
    if done_filter != 0:
        tasks_query = tasks_query.filter_by(done=done_filter > 0)
    tasks: list[Task] = tasks_query.all()
    return jsonify([task.as_dict for task in tasks])


@main.route("/profile")
@login_required
def profile():
    """Stránka s uživatelovými úkoly."""
    user_tasks_query: list[Task] = (Task.query
                                    .filter_by(user_id=current_user.id)
                                    .order_by(Task.created_at.desc())
                                    .all())
    user_tasks = [task.as_dict for task in user_tasks_query]
    return render_template("profile.html", user_tasks=user_tasks)


@main.route("/add_task", methods=["POST"])
@login_required
def add_task():
    """Přidat nový úkol."""
    new_task_content = request.form.get("new_task_content")
    if not new_task_content:
        flash("Nelze přidat prázdný úkol.")
        return redirect(url_for("main.profile"))

    new_task = Task(content=new_task_content, created_at=datetime.now(), done=False, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("main.profile"))


@main.route("/edit_task/<task_id>", methods=["POST"])
@login_required
def edit_task(task_id):
    """Upravit existující úkol."""
    edited_task_content = request.form.get("edited_task_content")
    if not edited_task_content:
        flash("Úkol nemůže být prázdný.")
        return redirect(url_for("main.profile"))

    task: Optional[Task] = Task.query.filter_by(id=task_id).first()
    if not task or task.user_id != current_user.id:
        flash("Úkol se nepodařilo změnit.")
        return redirect(url_for("main.profile"))

    task.content = edited_task_content
    db.session.commit()
    return redirect(url_for("main.profile"))


@main.route("/delete_task/<task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    """Smazat úkol."""
    task: Optional[Task] = Task.query.filter_by(id=task_id).first()
    if not task or task.user_id != current_user.id:
        flash("Úkol se nepodařilo smazat.")
        return redirect(url_for("main.profile"))

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("main.profile"))


@main.route("/complete_task/<task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    """Označit úkol jako (ne)dokončený."""
    task: Optional[Task] = Task.query.filter_by(id=task_id).first()
    if not task or task.user_id != current_user.id:
        flash("Úkol se nepodařilo upravit.")
        return redirect(url_for("main.profile"))

    task.done = not task.done
    db.session.commit()
    return redirect(url_for("main.profile"))
