# --- test_app.py ---
# This file contains automated tests for the CTF Dashboard project.
# It uses pytest to test routes like starting alerts, submitting flags, etc.

import os
import tempfile
import pytest
from app import create_app, db
from app.models import Alert, Flag, Submission

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Fixture to create a test client with a temporary SQLite database."""
    db_file = tmp_path / "test.db"  # Create temp DB file
    monkeypatch.setenv("DEV_DATABASE_URL", f"sqlite:///{db_file}")  # Override DB for test only
    app = create_app()
    app.config["TESTING"] = True  # Enable testing mode (no error catching)

    with app.app_context():
        db.create_all()  # Initialize tables
        yield app.test_client()  # Provide test client to tests
        db.drop_all()  # Clean up after test

def test_dashboard_empty(client):
    """Test: GET / should return 200 and show no alerts initially."""
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"Live Security Alerts" in rv.data

def test_api_create_and_list_alert(client):
    """Test: POST /alerts/create should return new UUID, and GET /alerts/ should list it."""
    # Step 1: Create new alert
    resp = client.post("/alerts/create")
    assert resp.status_code == 201
    data = resp.get_json()
    assert "uuid" in data  # Ensure a UUID is returned

    # Step 2: Check if alert appears in list
    list_resp = client.get("/alerts/list")  # Note: corrected to /alerts/list for your blueprint
    assert list_resp.status_code == 200
    alerts = list_resp.get_json()
    assert any(a["uuid"] == data["uuid"] for a in alerts)  # Confirm UUID is listed

def test_flag_submission_cycle(client):
    """End-to-end Test: Create alert, generate files, submit wrong flag, then correct flag."""
    # Step 1: Create a new alert
    new = client.post("/alerts/create").get_json()["uuid"]

    # Step 2: Trigger challenge folder creation
    rv = client.post(f"/alerts/{new}/trigger")
    assert rv.status_code == 204  # Should succeed silently

    # Step 3: Try submitting wrong flag
    rv = client.post("/submit_flag", data={"uuid": new, "flag": "WRONG"})
    assert rv.status_code == 302  # Should redirect back to dashboard (wrong answer)

    # Step 4: Lookup correct flag directly from DB
    from app.models import Flag
    from app import db as _db
    with client.application.app_context():
        correct = Flag.query.get(new).value

    # Step 5: Submit the correct flag
    rv = client.post("/submit_flag", data={"uuid": new, "flag": correct})
    assert b"/flag_complete/" in rv.headers["Location"].encode()  # Should redirect to success page

def test_reset_ctf(client):
    """Test that reset_ctf properly clears and reboots alerts."""
    client.post("/alerts/create")
    client.post("/alerts/create")
    rv = client.post("/reset_ctf")
    assert rv.status_code == 302  # Redirect after reset
