"""
tests/test_portal.py - end-to-end tests of the Flask portal using Flask's test client.

The test client sends REAL HTTP-style requests into the REAL application code
(routes -> validation -> SQLite -> template). No mocking.
"""

import pytest

from app import create_app
import database


# --------------------------------------------------------------------------- #
# The three REQUIRED lab tests
# --------------------------------------------------------------------------- #
def test_01_valid_submission_is_saved_and_displayed(client, valid_form, count):
    """TEST 1: complete student information with a valid URL -> saved and displayed."""
    response = client.post("/submit", data=valid_form, follow_redirects=True)

    assert response.status_code == 200
    assert count() == 1, "A valid submission should be stored in SQLite"
    page = response.get_data(as_text=True)
    assert "Submission received!" in page
    assert valid_form["student_name"] in page
    assert valid_form["registration_number"] in page
    assert valid_form["assignment_title"] in page
    assert valid_form["submission_url"] in page
    assert "Total submissions: <strong>1</strong>" in page


def test_02_missing_registration_number_is_rejected(client, valid_form, count):
    """TEST 2: missing registration number -> rejected with a message and NOT saved."""
    form = dict(valid_form, registration_number="")
    response = client.post("/submit", data=form)

    page = response.get_data(as_text=True)
    assert response.status_code == 400, "Missing registration number must be rejected (HTTP 400)"
    assert "Registration number is required." in page, "A validation message must be shown"
    assert count() == 0, "A submission without a registration number must NOT be saved"


def test_03_invalid_url_is_rejected(client, valid_form, count):
    """TEST 3: invalid submission URL -> rejected and NOT saved."""
    form = dict(valid_form, submission_url="not-a-valid-url")
    response = client.post("/submit", data=form)

    page = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "Please enter a valid URL" in page
    assert count() == 0, "A submission with an invalid URL must NOT be saved"


# --------------------------------------------------------------------------- #
# Additional tests
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("field, message", [
    ("student_name", "Student full name is required."),
    ("registration_number", "Registration number is required."),
    ("assignment_title", "Assignment title is required."),
    ("submission_url", "Submission URL is required."),
])
def test_each_missing_field_is_rejected(client, valid_form, count, field, message):
    response = client.post("/submit", data=dict(valid_form, **{field: ""}))
    assert response.status_code == 400
    assert message in response.get_data(as_text=True)
    assert count() == 0


def test_field_missing_from_request_entirely_is_rejected(client, valid_form, count):
    form = dict(valid_form)
    del form["registration_number"]
    response = client.post("/submit", data=form)
    assert response.status_code == 400
    assert count() == 0


def test_whitespace_only_registration_number_is_rejected(client, valid_form, count):
    response = client.post("/submit", data=dict(valid_form, registration_number="    "))
    assert response.status_code == 400
    assert "Registration number is required." in response.get_data(as_text=True)
    assert count() == 0


@pytest.mark.parametrize("bad_url", [
    "ftp://files.example.com/assignment.zip",
    "javascript:alert(1)",
    "mailto:teacher@example.com",
    "file:///C:/Users/student/assignment.docx",
    "www.github.com/student/repo",
    "https://",
    "http://exa mple.com",
    "https://localhost:notaport/x",
    "https://nodot",
])
def test_invalid_url_schemes_and_formats_are_rejected(client, valid_form, count, bad_url):
    response = client.post("/submit", data=dict(valid_form, submission_url=bad_url))
    assert response.status_code == 400, f"{bad_url!r} should be rejected"
    assert count() == 0


@pytest.mark.parametrize("good_url", [
    "http://example.com",
    "https://github.com/student/repo",
    "https://drive.google.com/file/d/abc123/view?usp=sharing",
    "HTTPS://Example.ORG/path",
])
def test_valid_http_and_https_urls_are_accepted(client, valid_form, count, good_url):
    response = client.post("/submit", data=dict(valid_form, submission_url=good_url))
    assert response.status_code == 302
    assert count() == 1


def test_invalid_submission_keeps_user_input_in_form(client, valid_form):
    response = client.post("/submit", data=dict(valid_form, submission_url="bad"))
    page = response.get_data(as_text=True)
    assert 'value="Ayesha Khan"' in page
    assert 'value="FA22-BSE-001"' in page


def test_values_are_trimmed_before_saving(client, valid_form, db_path):
    padded = {k: f"   {v}   " for k, v in valid_form.items()}
    client.post("/submit", data=padded)
    saved = database.list_submissions(db_path)[0]
    assert saved["student_name"] == "Ayesha Khan"
    assert saved["submission_url"] == valid_form["submission_url"]


def test_submission_has_date_and_time(client, valid_form, db_path):
    client.post("/submit", data=valid_form)
    saved = database.list_submissions(db_path)[0]
    assert saved["submitted_at"], "submitted_at timestamp must be stored"
    page = client.get("/").get_data(as_text=True)
    assert f'datetime="{saved["submitted_at"]}"' in page


def test_total_count_increases_with_each_submission(client, valid_form, count):
    for i in range(3):
        client.post("/submit", data=dict(valid_form, assignment_title=f"Lab {i + 1}"))
    assert count() == 3
    page = client.get("/").get_data(as_text=True)
    assert "Total submissions: <strong>3</strong>" in page
    assert page.count('data-testid="submission-row"') == 3


def test_data_persists_after_application_restart(db_path, valid_form):
    """Simulate a restart: create a brand-new app object pointing at the same DB file."""
    first_app = create_app({"TESTING": True, "DATABASE": db_path})
    first_app.test_client().post("/submit", data=valid_form)
    del first_app

    restarted_app = create_app({"TESTING": True, "DATABASE": db_path})
    page = restarted_app.test_client().get("/").get_data(as_text=True)
    assert valid_form["assignment_title"] in page
    assert "Total submissions: <strong>1</strong>" in page


def test_html_in_input_is_escaped(client, valid_form):
    client.post("/submit", data=dict(valid_form, student_name="<script>alert(1)</script>"))
    page = client.get("/").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_home_page_shows_empty_state(client):
    page = client.get("/").get_data(as_text=True)
    assert "No submissions yet" in page
    assert "Total submissions: <strong>0</strong>" in page


def test_health_endpoint(client, valid_form):
    client.post("/submit", data=valid_form)
    data = client.get("/health").get_json()
    assert data == {"status": "ok", "total_submissions": 1}


def test_get_on_submit_is_not_allowed(client):
    assert client.get("/submit").status_code == 405
