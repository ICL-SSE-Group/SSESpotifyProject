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
        print(f"Failed to fetch token: {response.status_code}, {response.text}")
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

    # Log the raw response for debugging
    print(f"Top tracks response: {data}")

    return [
        {
            "track": track["name"],
            "album": track["album"]["name"],  # Get the album name from the API response
        }
        for track in data["tracks"]
    ]

def get_track_details(token, track_id):
    """Fetch track details using Spotify API"""
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)

    # Log the raw response for debugging
    print(f"Track details response: {response.json()}")

    # Check if the response is successful
    if response.status_code == 200:
        track_data = response.json()
        popularity = track_data.get('popularity', 0)  # Default to 0 if popularity is missing
        return popularity
    else:
        return None  # Return None if there is an error

