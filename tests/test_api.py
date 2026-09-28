import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(original_activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


def test_get_activities_returns_activity_catalog():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_succeeds_and_prevents_duplicates():
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities_after_signup = client.get("/activities").json()
    assert email in activities_after_signup[activity_name]["participants"]

    duplicate_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    response = client.post("/activities/Nonexistent Club/signup?email=test@example.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_student_and_rejects_missing_participant():
    email = "daniel@mergington.edu"
    activity_name = "Chess Club"

    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{email.replace('@', '%40')}"
    )
    assert delete_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]

    missing_response = client.delete(
        f"/activities/{activity_name}/participants/{email.replace('@', '%40')}"
    )
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Participant not found in this activity"
