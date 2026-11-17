"""
tests/conftest.py - shared test fixtures.

Every test gets its OWN temporary SQLite database inside pytest's tmp_path,
so tests never touch your real instance/portal.db and never affect each other.
"""

import os
import sys

import pytest

# Make the project root importable (app.py, validation.py, receiver.py ...).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app  # noqa: E402
import database  # noqa: E402


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_portal.db")


@pytest.fixture
def app(db_path):
    return create_app({"TESTING": True, "DATABASE": db_path, "SECRET_KEY": "test"})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def valid_form():
    return {
        "student_name": "Ayesha Khan",
        "registration_number": "FA22-BSE-001",
        "assignment_title": "DevOps Mid Lab - CI/CD Pipeline",
        "submission_url": "https://github.com/ayesha-khan/devops-mid-lab",
    }


@pytest.fixture
def count(db_path):
    """Helper: count rows in the test database."""
    return lambda: database.count_submissions(db_path)
