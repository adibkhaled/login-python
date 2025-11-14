from flask import Blueprint, render_template, request, redirect, session, current_app
import bcrypt
from src import dbhelper as db

bp = Blueprint("login", __name__)

@bp.route("/", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            msg = "Provide username and password."
            return render_template("login.html", msg=msg)

        row = db.execute_query(
            "SELECT password_hash FROM users WHERE username = %s", (username,), fetchone=True
        )

        if row:
            stored_hash = row[0]
            try:
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    session["user"] = username
                    return redirect("/home")
            except Exception:
                current_app.logger.exception("Password check failed")

        msg = "Invalid username or password"

    return render_template("login.html", msg=msg)

@bp.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("home.html", user=session["user"])


@bp.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            msg = "Provide username and password."
            return render_template("register.html", msg=msg)

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        try:
            res = db.execute_query(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed),
                commit=True,
            )
            if res:
                msg = "Registered successfully!"
            else:
                msg = "Registration failed, check server logs."
        except Exception:
            # UniqueViolation will be visible via psycopg2 exception, but keep generic here
            current_app.logger.exception("Registration error")
            msg = "Registration failed."

    return render_template("register.html", msg=msg)