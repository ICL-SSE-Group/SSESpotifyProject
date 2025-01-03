import pytest
from spotify.app import app, init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    # Initialize the database before running tests
    init_db()

    with app.test_client() as client:
        yield client


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Enter the name of up to three artists " in response.data
    assert b"to see their top tracks:"


def test_query_real_artist(client):
    import os
    from spotify.APIQueries import get_token

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not client_id or not client_secret:
        pytest.skip(
            "Spotify API credentials are not set. Skipping real API test.")

    token = get_token(client_id, client_secret)
    assert token is not None, "Failed to retrieve Spotify token."

    artist_name = "Taylor Swift"

    response = client.post("/query", data={
        "spotify_artist1": artist_name,
        "spotify_artist2": "",
        "spotify_artist3": "",
    })

    assert response.status_code == 200
    assert b"Taylor Swift" in response.data


def test_query_no_artist(client):
    response = client.post("/query", data={
        "spotify_artist1": "",
        "spotify_artist2": "",
        "spotify_artist3": "",
    })
    assert response.status_code == 200
    assert b"Please enter at least one artist name!" in response.data


def test_save_tracks(client):
    response = client.post("/save_tracks", json={
        "selectedTracks": [
            {"id": "1",
             "track": "Mr. Brightside",
             "artist": "The Killers",
             "album_name": "Hot Fuss",
             "album_id": "4piJq7R3gjUOxnYs6lDCTg"},
            {"id": "2",
             "track": "Dreams",
             "artist": "Fleetwood Mac",
             "album_name": "Rumours",
             "album_id": "1bt6q2SruMsBtcerNVtpZB"}
        ]
    })
    assert response.status_code == 200


def test_save_tracks_no_tracks(client):
    response = client.post("/save_tracks", json={"selectedTracks": []})
    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_save_tracks_duplicates(client):
    response = client.post("/save_tracks", json={
        "selectedTracks": [
            {"id": "1",
             "track": "Mr. Brightside",
             "artist": "The Killers",
             "album_name": "Hot Fuss",
             "album_id": "4piJq7R3gjUOxnYs6lDCTg"},
            {"id": "1",
             "track": "Mr. Brightside",
             "artist": "The Killers",
             "album_name": "Hot Fuss",
             "album_id": "4piJq7R3gjUOxnYs6lDCTg"}
        ]
    })
    assert response.status_code == 200
    assert response.json["status"] == "success"


def test_ranking_no_tracks(client):
    response = client.get("/ranking")
    assert response.status_code == 302  # Redirects to homepage
    assert response.location.endswith("/")  # Redirect URL
