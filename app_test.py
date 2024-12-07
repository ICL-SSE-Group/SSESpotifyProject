import pytest
import sqlite3
from flask import session
from spotify.app import app, reset_tables, init_db
from spotify.APIQueries import artist_search, get_top_tracks

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    # Initialize the database before running tests
    init_db()

    with app.test_client() as client:
        yield client


# Test the homepage route
def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Enter the name of three artist in Spotify to see their top tracks" in response.data


def test_query_real_artist(client):
    import os
    from spotify.APIQueries import get_token

    # Load Spotify API credentials
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not client_id or not client_secret:
        pytest.skip("Spotify API credentials are not set. Skipping real API test.")

    # Retrieve a Spotify token
    token = get_token(client_id, client_secret)
    assert token is not None, "Failed to retrieve Spotify token."

    # Test with a real artist
    artist_name = "Taylor Swift"

    response = client.post("/query", data={
        "spotify_artist1": artist_name,
        "spotify_artist2": "",
        "spotify_artist3": "",
    })

    # Check the response
    assert response.status_code == 200
    assert b"Taylor Swift" in response.data  # Check if artist name appears


# Test save_tracks route
def test_save_tracks(client):
    response = client.post("/save_tracks", json={
        "selectedTracks": [
            {"id": "1", "track": "Track1", "artist": "Artist1"},
            {"id": "2", "track": "Track2", "artist": "Artist2"}
        ]
    })

    assert response.status_code == 200
    assert response.json["status"] == "success"


#def test_query_invalid_artist(client):
    # Test with an invalid artist
    #invalid_artist_name = "ThisArtistDoesNotExist12345"

    #response = client.post("/query", data={
        #"spotify_artist1": invalid_artist_name,
        #"spotify_artist2": "",
        #"spotify_artist3": "",
    #})

    # Check the response
    #assert response.status_code == 200
    #assert b"Artist not found" in response.data  # Check if the error message appears
