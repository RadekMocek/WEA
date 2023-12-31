from flask import Blueprint, flash, redirect, url_for

error = Blueprint("error", __name__)


@error.app_errorhandler(404)
def page_not_found(e):
    flash("[404] Požadovaná stránka nebyla nalezena.")
    return redirect(url_for("main.index"))


@error.app_errorhandler(405)
def method_not_allowed(e):
    flash("[405] Pro práci s úkoly využijte uživatelského rozhraní.")
    return redirect(url_for("main.index"))
