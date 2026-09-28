from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


def test_unregister_participant_from_activity():
    # Arrange
    email = "newstudent_app@mergington.edu"
    activity_name = "Chess Club"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={email}",
    )
    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{email.replace('@', '%40')}"
    )

    # Assert
    assert signup_response.status_code == 200
    assert delete_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]
