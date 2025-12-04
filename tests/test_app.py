"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that activities contain expected fields"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        
        activity = activities["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_returns_200(self):
        """Test that signing up a new participant returns status 200"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_new_participant_returns_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent2@mergington.edu"
        )
        assert "message" in response.json()
        assert "Signed up" in response.json()["message"]

    def test_signup_duplicate_participant_returns_400(self):
        """Test that signing up an already registered participant returns 400"""
        # First signup should succeed
        client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
        
        # Second signup with same email should fail
        response = client.post(
            "/activities/Chess%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signing up for a nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_registered_participant_returns_200(self):
        """Test that unregistering a registered participant returns status 200"""
        # First signup
        client.post("/activities/Chess%20Club/signup?email=tounregister@mergington.edu")
        
        # Then unregister
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=tounregister@mergington.edu"
        )
        assert response.status_code == 200

    def test_unregister_returns_message(self):
        """Test that unregister returns a success message"""
        # First signup
        client.post(
            "/activities/Programming%20Class/signup?email=toremove@mergington.edu"
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Programming%20Class/unregister?email=toremove@mergington.edu"
        )
        assert "message" in response.json()
        assert "Unregistered" in response.json()["message"]

    def test_unregister_not_registered_participant_returns_400(self):
        """Test that unregistering a non-registered participant returns 400"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregistering from a nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        # First signup
        client.post(
            "/activities/Gym%20Class/signup?email=tocheck@mergington.edu"
        )
        
        # Verify participant is in the list
        response = client.get("/activities")
        assert "tocheck@mergington.edu" in response.json()["Gym Class"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Gym%20Class/unregister?email=tocheck@mergington.edu"
        )
        
        # Verify participant is removed
        response = client.get("/activities")
        assert "tocheck@mergington.edu" not in response.json()["Gym Class"]["participants"]
