import pytest
from app import app
import json
from unittest.mock import patch


@pytest.fixture
def client():
    """Set up the test client for the Flask app."""
    app.testing = True
    client = app.test_client()
    yield client


def test_home_page(client):
    """Test the home page route."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Get Artist's Top Tracks" in response.data


@patch("app.requests.get")
def test_get_tracks(mock_get, client):
    """Test the /get-tracks endpoint."""
    # Mock the API response
    mock_response = {
        "tracks": [
            {"name": "Song 1", "id": "1"},
            {"name": "Song 2", "id": "2"},
            {"name": "Song 3", "id": "3"},
        ]
    }
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    # Send a POST request to /get-tracks
    response = client.post("/get-tracks", json={"artist_name": "Oasis"})
    assert response.status_code == 200

    # Verify the response contains track data
    data = response.get_json()
    assert "tracks" in data
    assert len(data["tracks"]) > 0


def test_submit_guess(client):
    """Test the /submit-guess endpoint."""
    # Example data for the POST request
    mock_data = {
        "user_guesses": ["Song 1", "Song 2", "Song 3", "Song 4", "Song 5"],
        "correct_tracks": ["Song 1", "Song 3", "Song 5", "Song 6", "Song 7"],
    }

    response = client.post(
        "/submit-guess",
        data=json.dumps(mock_data),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert b"Your Score" in response.data


def test_error_handling(client):
    """Test for proper error handling when no artist is provided."""
    response = client.post("/get-tracks", json={"artist_name": ""})
    assert response.status_code == 400
    assert b"Error: Artist name is required" in response.data
