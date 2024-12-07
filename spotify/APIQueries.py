import base64
import requests


def get_token(client_id, client_secret):
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
    return {
        "Authorization": f"Bearer {token}",
    }


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

    return [
        {
            "track": track["name"],
            "album": track["album"]["name"],
            "popularity": track["popularity"],
            "album_id": track["album"]["id"]
        }
        for track in data["tracks"]
    ]



def get_tracks_by_album(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = get_auth_header(token)
    params = {"market": "US"}  # Optional: You can specify a market to limit the results to a region

    # Send the request to get album tracks
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # Debugging: Print the response
    print(f"Album tracks response: {data}")

    return [
        {
            "track": track["name"],
            #"album": track.get("album", {}).get("name", "Unknown Album"),  # Safely get album name, fallback to "Unknown Album"
            #"popularity": track.get("popularity", "Unknown"),  # Handle missing popularity
            #"album_id": album_id  # Pass album_id as it's known
        }
        for track in data.get("items", [])  # Safely access "items" in case it's missing
    ]


