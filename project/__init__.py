from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    # Flask aplikace
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secretbruh"  # TODO
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

    # Databáze
    db.init_app(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Tato akce vyžaduje přihlášení."
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .error import error as error_blueprint
    app.register_blueprint(error_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Databáze II
    with app.app_context():
        db.create_all()

    return app
