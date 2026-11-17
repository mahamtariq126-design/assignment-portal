"""tests/test_validation.py - unit tests for validation.py (no web server involved)."""

import pytest

from validation import is_valid_url, validate_submission


def test_complete_form_has_no_errors():
    data, errors = validate_submission({
        "student_name": "Ali Raza",
        "registration_number": "SP23-BCS-045",
        "assignment_title": "Lab 4",
        "submission_url": "https://github.com/ali/lab4",
    })
    assert errors == {}
    assert data["registration_number"] == "SP23-BCS-045"


def test_missing_registration_number_produces_error():
    _, errors = validate_submission({
        "student_name": "Ali Raza",
        "registration_number": "",
        "assignment_title": "Lab 4",
        "submission_url": "https://github.com/ali/lab4",
    })
    assert errors.get("registration_number") == "Registration number is required."


def test_empty_form_reports_all_four_fields():
    _, errors = validate_submission({})
    assert set(errors) == {"student_name", "registration_number", "assignment_title", "submission_url"}


@pytest.mark.parametrize("reg", ["FA22-BSE-001", "2022/CS/045", "SP23_BCS_12", "ab"])
def test_registration_number_formats_accepted(reg):
    _, errors = validate_submission({"registration_number": reg})
    assert "registration_number" not in errors


@pytest.mark.parametrize("reg", ["-FA22", "FA22<script>", pytest.param("x" * 31, id="31-chars-too-long"), "A"])
def test_registration_number_formats_rejected(reg):
    _, errors = validate_submission({"registration_number": reg})
    assert "registration_number" in errors


@pytest.mark.parametrize("url, expected", [
    ("https://github.com/a/b", True),
    ("http://localhost:5000/x", True),
    ("http://192.168.1.10/report", True),
    ("http://999.1.1.1/", False),
    ("https://-bad-.com", False),
    ("ftp://example.com", False),
    ("", False),
    pytest.param("https://example.com/" + "a" * 600, False, id="url-longer-than-500-chars"),
])
def test_is_valid_url(url, expected):
    assert is_valid_url(url) is expected
