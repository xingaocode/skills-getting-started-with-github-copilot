import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    # Use a unique email to avoid duplicate error
    response = client.post("/activities/Chess%20Club/signup?email=tester1@mergington.edu")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    # Clean up: remove the test participant
    data = client.get("/activities").json()
    data["Chess Club"]["participants"].remove("tester1@mergington.edu")

def test_signup_duplicate():
    # Add a participant
    client.post("/activities/Chess%20Club/signup?email=tester2@mergington.edu")
    # Try to add again
    response = client.post("/activities/Chess%20Club/signup?email=tester2@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    # Clean up
    data = client.get("/activities").json()
    data["Chess Club"]["participants"].remove("tester2@mergington.edu")

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=ghost@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_signup_full_capacity():
    # Fill up the activity
    activity = client.get("/activities").json()["Debate Team"]
    max_participants = activity["max_participants"]
    # Add up to max
    for i in range(len(activity["participants"]), max_participants):
        client.post(f"/activities/Debate%20Team/signup?email=full{i}@mergington.edu")
    # Now try one more
    response = client.post("/activities/Debate%20Team/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert "full capacity" in response.json()["detail"]
    # Clean up
    data = client.get("/activities").json()
    for i in range(len(data["Debate Team"]["participants"])-max_participants, 0, -1):
        email = f"full{i+len(activity['participants'])-1}@mergington.edu"
        if email in data["Debate Team"]["participants"]:
            data["Debate Team"]["participants"].remove(email)
