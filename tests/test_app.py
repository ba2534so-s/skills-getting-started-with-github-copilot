"""
Test suite for the Mergington High School Activities API.
"""
from fastapi.testclient import TestClient
import pytest
from src.app import app, activities

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def test_activity():
    """Get a test activity name."""
    return next(iter(activities.keys()))


def test_root_redirects_to_static(client):
    """Test that root URL redirects to static/index.html."""
    response = client.get("/")
    assert response.status_code == 200  # Direct file serving in test environment
    assert "text/html" in response.headers["content-type"].lower()


def test_get_activities(client):
    """Test getting the list of activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Check structure of an activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_signup_for_activity_success(client, test_activity):
    """Test successful signup for an activity."""
    test_email = "newstudent@mergington.edu"
    
    # Ensure the student isn't already signed up
    if test_email in activities[test_activity]["participants"]:
        activities[test_activity]["participants"].remove(test_email)
    
    response = client.post(f"/activities/{test_activity}/signup?email={test_email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert test_email in data["message"]
    assert test_activity in data["message"]
    
    # Verify student was added to participants
    assert test_email in activities[test_activity]["participants"]


def test_signup_for_activity_duplicate(client, test_activity):
    """Test signup attempt for already registered student."""
    test_email = "duplicate@mergington.edu"
    
    # First signup
    client.post(f"/activities/{test_activity}/signup?email={test_email}")
    
    # Try to signup again
    response = client.post(f"/activities/{test_activity}/signup?email={test_email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_for_nonexistent_activity(client):
    """Test signup attempt for non-existent activity."""
    response = client.post("/activities/NonExistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_from_activity_success(client, test_activity):
    """Test successful unregistration from an activity."""
    test_email = "tounregister@mergington.edu"
    
    # First register the student
    client.post(f"/activities/{test_activity}/signup?email={test_email}")
    
    # Then unregister
    response = client.post(f"/activities/{test_activity}/unregister?email={test_email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert test_email in data["message"]
    assert test_activity in data["message"]
    
    # Verify student was removed from participants
    assert test_email not in activities[test_activity]["participants"]
def test_unregister_not_registered(client, test_activity):
    """Test unregistration attempt for student not registered in activity."""
    test_email = "notregistered@mergington.edu"
    
    response = client.post(f"/activities/{test_activity}/unregister?email={test_email}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not registered" in data["detail"].lower()