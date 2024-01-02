"""Endpointy pro přihlášení/registraci/odhlášení uživatelů."""

from typing import Optional

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import User

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    """Stránka pro přihlášení."""
    if current_user.is_authenticated:
        flash("Již jste přihlášen/a.")
        return redirect(url_for('main.index'))
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    """Přihlášení uživatele."""
    nickname = request.form.get("nickname")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    # Existuje uživatel a shodují se hashe hesel ?
    user: Optional[User] = User.query.filter_by(nickname=nickname).first()
    if not user or not check_password_hash(user.password, password):
        flash("Neplatné uživatelské jméno nebo heslo.")
        return redirect(url_for("auth.login"))

    login_user(user, remember=remember)
    return redirect(url_for("main.profile"))


@auth.route("/signup")
def signup():
    """Stránka pro registraci."""
    if current_user.is_authenticated:
        flash("Již jste přihlášen/a.")
        return redirect(url_for('main.index'))
    return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
    """Registrace uživatele."""
    nickname = request.form.get("nickname")
    password = request.form.get("password")
    password_check = request.form.get("password_check")

    # Shodují se dvě zadaná hesla ?
    if password != password_check:
        flash("Zadaná hesla se neshodují.")
        return redirect(url_for("auth.signup"))

    # Má heslo dostatečnou délku ?
    min_len = 8
    if len(password) < min_len:
        flash(f"Heslo musí mít alsepoň {min_len} znaků.")
        return redirect(url_for("auth.signup"))

    # Neexistuje už uživatel s takovýmto nickname ?
    user = User.query.filter_by(nickname=nickname).first()
    if user:
        flash("Toto uživatelské jméno není dostupné.")
        return redirect(url_for("auth.signup"))

    # Přidat uživatele do databáze
    new_user = User(nickname=nickname, password=generate_password_hash(password, method="scrypt"))
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))


@auth.route("/logout")
@login_required
def logout():
    """Odhlášení uživatele."""
    logout_user()
    return redirect(url_for('main.index'))
