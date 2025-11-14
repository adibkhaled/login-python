from flask import Blueprint, render_template, request, session, redirect, current_app
import requests
import json

bp = Blueprint("licence", __name__)


@bp.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("home.html", user=session["user"])

@bp.route("/licence", methods=["GET", "POST"])
def licence_lookup():
    result = None
    error = None
    license_plate = ""

    if request.method == "POST":
        license_plate = (request.form.get("licensePlate") or "").strip()
        if not license_plate:
            error = "Please provide a license plate."
        else:
            # protect single quotes for Socrata $where clause
            safe_plate = license_plate.replace("'", "''")
            params = {
                "$where": f"(UPPER(kenteken)=UPPER('{safe_plate}'))",
                "$limit": "1"
            }
            url = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"
            try:
                resp = requests.get(url, params=params, timeout=6)
                resp.raise_for_status()
                data = resp.json()
                if not data:
                    error = "No record found for that license plate."
                else:
                    # pretty JSON for display and a simple dict for individual fields
                    result = {
                        "record": data[0],
                        "pretty": json.dumps(data[0], indent=2, ensure_ascii=False)
                    }
            except requests.exceptions.RequestException as e:
                current_app.logger.exception("RDW API request failed")
                error = f"Lookup failed: {e}"

    return render_template(
        "licence.html",
        user=session["user"],
        license_plate=license_plate,
        result=result,
        error=error
    )