import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Check if we have the expected activities
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    
    # Check structure of an activity
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success():
    activity = "Chess Club"
    email = "test@mergington.edu"
    
    # Try to sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Successfully signed up for {activity}"
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity]["participants"]

def test_signup_full_activity():
    activity = "Chess Club"
    # Fill up the activity
    current_participants = client.get("/activities").json()[activity]["participants"]
    max_participants = client.get("/activities").json()[activity]["max_participants"]
    
    # Add participants until full
    for i in range(max_participants - len(current_participants)):
        email = f"filler{i}@mergington.edu"
        client.post(f"/activities/{activity}/signup?email={email}")
    
    # Try to sign up when full
    response = client.post(f"/activities/{activity}/signup?email=extra@mergington.edu")
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()

def test_signup_duplicate():
    activity = "Programming Class"
    email = "duplicate@mergington.edu"
    
    # Sign up first time
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Try to sign up again
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_unregister_success():
    activity = "Programming Class"
    email = "emma@mergington.edu"  # Using an existing participant
    
    # Try to unregister
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Successfully unregistered from {activity}"
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity]["participants"]

def test_unregister_not_registered():
    activity = "Programming Class"
    email = "notregistered@mergington.edu"
    
    # Try to unregister
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_invalid_activity():
    activity = "Non-Existent Club"
    email = "test@mergington.edu"
    
    # Try to sign up for non-existent activity
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()