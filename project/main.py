from datetime import datetime
from typing import Optional

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import Task

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/get_tasks_json")
def get_tasks_json():
    tasks: list[Task] = Task.query.all()
    return jsonify([task.as_dict for task in tasks])


@main.route("/profile")
@login_required
def profile():
    # user_tasks_query = db.session.execute(db.select(Task).filter_by(user_id=current_user.id)).all()
    user_tasks_query: list[Task] = (Task.query
                                    .filter_by(user_id=current_user.id)
                                    .order_by(Task.created_at.desc())
                                    .all())
    user_tasks = [task.as_dict for task in user_tasks_query]
    return render_template("profile.html", user_tasks=user_tasks)


@main.route("/add_task", methods=["POST"])
@login_required
def add_task():
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
    task: Optional[Task] = Task.query.filter_by(id=task_id).first()
    if not task or task.user_id != current_user.id:
        flash("Úkol se nepodařilo smazat.")
        return redirect(url_for("main.profile"))

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("main.profile"))
