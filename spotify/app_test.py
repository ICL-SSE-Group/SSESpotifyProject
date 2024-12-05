import pytest
from flask import json
from app import app, init_db


# Fixture to set up the test client
@pytest.fixture(scope="module")
def test_client():
    flask_app = app
    flask_app.config["TESTING"] = True
    flask_app.config["DATABASE"] = "sqlite:///:memory:"  # In-memory DB

    # Initialize the database
    with flask_app.app_context():
        init_db()

    # Provide the test client
    with flask_app.test_client() as testing_client:
        yield testing_client


def test_index_route(test_client):
    """Test the home page route."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"Home" in response.data  # Update this to match index.html content


def test_query_route_valid_artist_mocked(test_client, monkeypatch):
    """Test the query route with valid artist input (mocked)."""

    def mock_artist_search(token, artist_name):
        return "mock_artist_id", artist_name

    def mock_get_top_tracks(token, artist_id):
        return ["Track 1", "Track 2", "Track 3"]

    monkeypatch.setattr("spotify.APIQueries.artist_search", mock_artist_search)
    monkeypatch.setattr(
        "spotify.APIQueries.get_top_tracks", mock_get_top_tracks)

    data = {
        "spotify_artist1": "Mock Artist",
        "spotify_artist2": "",
        "spotify_artist3": ""
    }
    response = test_client.post(
        "/query",
        data=data
    )

    assert response.status_code == 200
    assert b"Mock Artist" in response.data
    assert b"Track 1" in response.data


def test_query_route_with_real_artist(test_client):
    """Test the query route using a real artist."""
    data = {
        "spotify_artist1": "Taylor Swift",
        "spotify_artist2": "",
        "spotify_artist3": ""
    }

    response = test_client.post(
        "/query",
        data=data
    )

    assert response.status_code == 200
    assert b"Taylor Swift" in response.data


def test_query_route_no_artist(test_client):
    """Test the query route with no artist input."""
    data = {}
    response = test_client.post("/query", data=data)

    assert response.status_code == 200
    assert b"Please enter at least one artist name!" in response.data


def test_save_tracks_route(test_client, monkeypatch):
    """Test the save_tracks route."""

    def mock_audio_features(token, track_id):
        return {"danceability": 0.85}

    def mock_insert_song(song_id, song_name, artist_name, danceability):
        pass  # Mock database insertion

    monkeypatch.setattr(
        "spotify.APIQueries.audio_features",
        mock_audio_features
    )
    monkeypatch.setattr(
        "spotify.databases.insert_song",
        mock_insert_song
    )

    data = {
        "selectedTracks": [
            {"id": "track1", "name": "Track 1", "artist": "Artist 1"},
            {"id": "track2", "name": "Track 2", "artist": "Artist 2"},
        ]
    }

    response = test_client.post(
        "/save_tracks",
        data=json.dumps(data),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert b"Tracks saved successfully!" in response.data


def test_view_playlist_route_mocked(test_client, monkeypatch):
    """Test the view_playlist route (mocked)."""

    def mock_fetch_all_songs():
        return [
            {
                "id": "track1",
                "name": "Track 1",
                "artist": "Artist 1",
                "danceability": 0.9,
            },
            {
                "id": "track2",
                "name": "Track 2",
                "artist": "Artist 2",
                "danceability": 0.7,
            },
        ]

    monkeypatch.setattr(
        "spotify.databases.fetch_all_songs",
        mock_fetch_all_songs
    )

    response = test_client.get("/ranking")

    assert response.status_code == 200
    assert b"Track 1" in response.data
    assert b"Artist 1" in response.data


def test_view_playlist_with_real_data(test_client):
    """Test the view_playlist route using real data."""
    response = test_client.get("/ranking")

    assert response.status_code == 200
    assert b"danceability" in response.data or b"Track" in response.data
