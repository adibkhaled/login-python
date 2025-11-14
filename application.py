# ...existing code...
from flask import Flask, render_template, request, redirect, session
import psycopg2
import psycopg2.errors
import bcrypt
import os
import logging

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")
app.logger.setLevel(logging.INFO)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "database": os.environ.get("DB_NAME", "appdb"),
    "user": os.environ.get("DB_USER", "appuser"),
    "password": os.environ.get("DB_PASSWORD", "apppassword"),
    # optional: add "connect_timeout": 5
}


def get_connection():
    """Create a new DB connection using environment config."""
    return psycopg2.connect(**DB_CONFIG)


def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Helper to run a query and return results.
    - fetchone: return single row
    - fetchall: return all rows
    - commit: commit transaction (use for INSERT/UPDATE/DELETE)
    """
    conn = None
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                if commit:
                    return True
                if fetchone:
                    return cur.fetchone()
                if fetchall:
                    return cur.fetchall()
                return None
    except Exception:
        app.logger.exception("Database error")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


@app.route("/", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            msg = "Provide username and password."
            return render_template("login.html", msg=msg)

        row = execute_query(
            "SELECT password_hash FROM users WHERE username = %s", (username,), fetchone=True
        )

        if row:
            stored_hash = row[0]
            try:
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    session["user"] = username
                    return redirect("/home")
            except Exception:
                app.logger.exception("Password check failed")

        msg = "Invalid username or password"

    return render_template("login.html", msg=msg)


@app.route("/register", methods=["GET", "POST"])
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
            res = execute_query(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed),
                commit=True,
            )
            if res:
                msg = "Registered successfully!"
            else:
                msg = "Registration failed, check server logs."
        except psycopg2.errors.UniqueViolation:
            app.logger.info("Attempt to register existing username: %s", username)
            msg = "Username already exists."
        except Exception:
            app.logger.exception("Registration error")
            msg = "Registration failed."

    return render_template("register.html", msg=msg)


@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return f"<h2>Welcome {session['user']}</h2><a href='/logout'>Logout</a>"


# ...existing code...
@app.route("/logout")
def logout():
    session.clear()
    # render a logout page that redirects back to the login page after a few seconds
    return render_template("logout.html", redirect_url="/", delay=3)
# ...existing code...


# ...existing code...
if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("FLASK_RUN_PORT", 5010)))
    debug = os.environ.get("FLASK_ENV", "").lower() == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)