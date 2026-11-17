"""
validation.py - All form validation rules for the Assignment Submission Portal.

Every rule lives here so that:
  * the Flask app (app.py) uses exactly the same rules as the tests, and
  * the "deliberate defect" demo (scripts/demo_defect.py) only has to touch
    one clearly marked line in this file.
"""

import re
from urllib.parse import urlparse

# Maximum lengths keep the database tidy and stop abuse.
MAX_NAME = 100
MAX_REG = 30
MAX_TITLE = 150
MAX_URL = 500

# Registration numbers such as "FA22-BSE-001", "2022/CS/045" or "SP23_BCS_12".
REG_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-/_. ]{1,29}$")

# A host name label: letters, digits and hyphens (not at the start/end).
HOST_LABEL = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)$")

ALLOWED_SCHEMES = ("http", "https")


def is_valid_url(value):
    """Return True only for well-formed http:// or https:// URLs."""
    if not value or len(value) > MAX_URL:
        return False
    if any(ch.isspace() for ch in value):
        return False

    try:
        parsed = urlparse(value)
    except ValueError:
        return False

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False
    if not parsed.netloc:
        return False

    try:
        host = parsed.hostname  # strips user:password@ and :port
        parsed.port              # raises ValueError if the port is not a number
    except ValueError:
        return False
    if not host:
        return False

    if host == "localhost":
        return True

    # IPv4 address such as 192.168.1.10
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
        return all(0 <= int(part) <= 255 for part in host.split("."))

    # Normal domain: needs at least one dot and a letter-only top-level domain.
    labels = host.split(".")
    if len(labels) < 2:
        return False
    if not all(HOST_LABEL.match(label) for label in labels):
        return False
    if not re.fullmatch(r"[A-Za-z]{2,63}", labels[-1]):
        return False
    return True


def validate_submission(form):
    """
    Validate the submitted form.

    Returns a tuple: (cleaned_data, errors)
      cleaned_data -> dict with whitespace-trimmed values
      errors       -> dict {field_name: "error message"}; empty when valid
    """
    data = {
        "student_name": (form.get("student_name") or "").strip(),
        "registration_number": (form.get("registration_number") or "").strip(),
        "assignment_title": (form.get("assignment_title") or "").strip(),
        "submission_url": (form.get("submission_url") or "").strip(),
    }
    errors = {}

    # 1. Student full name
    name = data["student_name"]
    if not name:
        errors["student_name"] = "Student full name is required."
    elif len(name) > MAX_NAME:
        errors["student_name"] = f"Name must be at most {MAX_NAME} characters."

    # 2. Registration number
    reg_no = data["registration_number"]
    if not reg_no:
        errors["registration_number"] = "Registration number is required."  # REG-REQUIRED-CHECK
    elif len(reg_no) > MAX_REG or not REG_PATTERN.match(reg_no):
        errors["registration_number"] = (
            "Registration number may contain only letters, digits, '-', '/', '_' "
            "or '.' (2-30 characters)."
        )

    # 3. Assignment title
    title = data["assignment_title"]
    if not title:
        errors["assignment_title"] = "Assignment title is required."
    elif len(title) > MAX_TITLE:
        errors["assignment_title"] = f"Title must be at most {MAX_TITLE} characters."

    # 4. Submission URL
    url = data["submission_url"]
    if not url:
        errors["submission_url"] = "Submission URL is required."
    elif not is_valid_url(url):
        errors["submission_url"] = (
            "Please enter a valid URL that starts with http:// or https:// "
            "(for example https://github.com/your-name/your-repo)."
        )

    return data, errors
