import base64
import requests


def get_token(client_id, client_secret):
    """Fetch an access token from Spotify's API using client credentials"""

    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode()
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        print(
            f"Failed to fetch token:{response.status_code}, {response.text}")
        response.raise_for_status()
    return response.json().get("access_token")


def get_auth_header(token):
    """Generate an authorization header using the access token."""
    return {
        "Authorization": f"Bearer {token}",
    }


def artist_search(token, artist_name):
    """Search for an artist by name using Spotify's API."""

    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1,
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if not data["artists"]["items"]:
        raise ValueError(f"Artist '{artist_name}' not found!")

    artist = data["artists"]["items"][0]
    return artist["id"], artist["name"]


def get_top_tracks(token, artist_id):
    """Fetch the top tracks of a given artist."""

    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(token)
    params = {"market": "US"}  # Required parameter for the API

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    return [
        {
            "track": track["name"],
            "album": track["album"]["name"],
            "popularity": track["popularity"],
            "album_id": track["album"]["id"],
            "release_date": track["album"]["release_date"]
        }
        for track in data["tracks"]
    ]


def get_tracks_by_album(token, album_id):
    """Fetch all tracks from a given album."""

    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = get_auth_header(token)
    params = {"market": "US"}  # optional

    # Send the request to get album tracks
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # Debugging: Print the response
    print(f"Album tracks response: {data}")

    return [
        {
            "track": track["name"],

        }
        for track in data.get("items", [])
    ]
