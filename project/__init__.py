"""Modul pro inicializaci a spuštění Flask webové aplikace."""

import pathlib
import secrets

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app():
    """Inicializace Flask aplikace."""
    app = Flask(__name__)

    # Secret key pro šifrování cookies atd.
    flask_secret_key_path = pathlib.Path(".flask_secret_key")
    try:  # Přečíst key ze (private) souboru
        with flask_secret_key_path.open("r") as secret_file:
            flask_secret_key = secret_file.read()
    except FileNotFoundError:  # Pokud soubor neexistuje – vygenerovat, uložit a použít nový key
        with flask_secret_key_path.open("w") as secret_file:
            flask_secret_key = secrets.token_hex(32)
            secret_file.write(flask_secret_key)
    app.config["SECRET_KEY"] = flask_secret_key

    # Jinja autoescaping by měl být automaticky zapnutý pro html soubory, pro jistotu ale zapneme pro všechno
    app.jinja_options["autoescape"] = lambda _: True

    # SQLite databáze spravovaná SQLAlchemy pro uživatele a jejich úkoly
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    db.init_app(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"  # Stránka pro přihlášení (modul auth.py funkce login)
    login_manager.login_message = "Tato akce vyžaduje přihlášení."
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Obrana proti CSRF
    csrf.init_app(app)

    # Blueprints umožňují rozdělení endpointů do více souborů
    # - Přihlášení / registrace / odhlášení
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    # - HTTP Error pages
    from .error import error as error_blueprint
    app.register_blueprint(error_blueprint)
    # - Úkoly CRUD
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Načtení / případné vytvoření databáze
    with app.app_context():
        db.create_all()

    return app
