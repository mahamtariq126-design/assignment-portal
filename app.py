"""
app.py - Assignment Submission Portal (Flask + SQLite).

Run it locally:
    python app.py
then open http://127.0.0.1:5000 in your browser.

How a request flows:
  GET  /        -> show the form, the total count and all saved submissions
  POST /submit  -> validate the form
                   * invalid -> show the form again with red error messages (HTTP 400)
                   * valid   -> save to SQLite, then redirect to / with a success banner
  GET  /health  -> tiny JSON "is the app alive?" check
"""

import os
from datetime import datetime

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

import database
from validation import validate_submission

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app(test_config=None):
    """Application factory: tests call create_app({...}) with their own temp database."""
    app = Flask(__name__, instance_path=os.path.join(BASE_DIR, "instance"))
    app.config.update(
        SECRET_KEY=os.environ.get("PORTAL_SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.environ.get("PORTAL_DB", os.path.join(app.instance_path, "portal.db")),
        UNIVERSITY_NAME=os.environ.get("PORTAL_UNIVERSITY", "Northbridge University"),
    )
    if test_config:
        app.config.update(test_config)

    db_dir = os.path.dirname(os.path.abspath(app.config["DATABASE"]))
    os.makedirs(db_dir, exist_ok=True)
    database.init_db(app.config["DATABASE"])

    @app.template_filter("pretty_time")
    def pretty_time(iso_value):
        """Convert the stored UTC time into this computer's local time for display."""
        try:
            local = datetime.fromisoformat(iso_value).astimezone()
            return local.strftime("%d %b %Y, %I:%M %p")
        except (TypeError, ValueError):
            return iso_value

    def render_portal(form_data=None, errors=None, status=200):
        db_path = app.config["DATABASE"]
        return (
            render_template(
                "index.html",
                submissions=database.list_submissions(db_path),
                total=database.count_submissions(db_path),
                form=form_data or {},
                errors=errors or {},
                university=app.config["UNIVERSITY_NAME"],
                just_submitted=request.args.get("submitted") == "1",
            ),
            status,
        )

    @app.route("/", methods=["GET"])
    def index():
        return render_portal()

    @app.route("/submit", methods=["POST"])
    def submit():
        data, errors = validate_submission(request.form)
        if errors:
            flash("Your submission was not saved. Please fix the highlighted fields.", "error")
            return render_portal(form_data=data, errors=errors, status=400)

        database.add_submission(app.config["DATABASE"], data)
        flash(
            f"Submission received! Thank you, {data['student_name']}. "
            f"'{data['assignment_title']}' has been recorded.",
            "success",
        )
        # Post/Redirect/Get: refreshing the page will not submit twice.
        return redirect(url_for("index", submitted=1) + "#submissions")

    @app.route("/health")
    def health():
        return jsonify(
            status="ok",
            total_submissions=database.count_submissions(app.config["DATABASE"]),
        )

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    create_app().run(host="127.0.0.1", port=port, debug=False)
