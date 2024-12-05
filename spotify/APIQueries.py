import base64
import requests


def get_token(client_id, client_secret):

    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode()
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": f"Basic {auth_base64}"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        print(
            f"Failed to fetch token: {response.status_code}, {response.text}")
        response.raise_for_status()
    return response.json().get("access_token")


def get_auth_header(token):

    return {"Authorization": f"Bearer {token}"}


def artist_search(token, artist_name):

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

    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(token)
    params = {"market": "US"}  # Required parameter for the API

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return [track["name"] for track in data["tracks"]]


def audio_features(token, track_id):

    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = get_auth_header(token)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
