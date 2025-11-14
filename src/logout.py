from flask import Blueprint, render_template, session, redirect

bp = Blueprint("logout", __name__)

@bp.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html", redirect_url="/", delay=3)