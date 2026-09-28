from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


def test_get_activities_returns_activity_catalog():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity in payload
    assert payload[expected_activity]["max_participants"] == 12
    assert payload[expected_activity]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_succeeds_and_prevents_duplicates():
    # Arrange
    email = "newstudent_api@mergington.edu"
    activity_name = "Chess Club"

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    activities_after_signup = client.get("/activities").json()
    duplicate_response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities_after_signup[activity_name]["participants"]
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    # Arrange
    missing_activity = "Nonexistent Club"
    email = "test@example.edu"

    # Act
    response = client.post(f"/activities/{missing_activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_student_and_rejects_missing_participant():
    # Arrange
    email = "daniel@mergington.edu"
    activity_name = "Chess Club"

    # Act
    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{email.replace('@', '%40')}"
    )
    activities_after_delete = client.get("/activities").json()
    missing_response = client.delete(
        f"/activities/{activity_name}/participants/{email.replace('@', '%40')}"
    )

    # Assert
    assert delete_response.status_code == 200
    assert email not in activities_after_delete[activity_name]["participants"]
    assert missing_response.status_code == 404
    assert missing_response.json()["detail"] == "Participant not found in this activity"
