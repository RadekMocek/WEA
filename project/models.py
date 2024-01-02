"""Definice databázových modelů."""

from flask_login import UserMixin

from . import db


class User(UserMixin, db.Model):
    """Uživatel"""
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    tasks = db.relationship("Task", backref="user")


class Task(db.Model):
    """Úkol"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1024))
    created_at = db.Column(db.DateTime)
    done = db.Column(db.Boolean)  # Je úkol označen jako dokončený ?
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    @property
    def as_dict(self):
        """Úkol převedený na slovník (potřebné pro JSON serializaci)."""
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
