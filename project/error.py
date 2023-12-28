from flask import Blueprint, flash, redirect, url_for

error = Blueprint("error", __name__)


@error.app_errorhandler(404)
def page_not_found(e):
    flash("Požadovaná stránka nebyla nalezena.")
    return redirect(url_for("main.index"))
