import requests

def get_auth_header(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def artist_search(token, artist_name):
    url = "https://api.spotify.com/v1/search" #endpoint for search for item function
    headers = get_auth_header(token) #create authorization header with access token

    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1,
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if not data['artists']['items']:
        raise ValueError("Artist not found!")

    # Get artist ID and name
    artist = data["artists"]["items"][0]
    return artist["id"], artist["name"]

def get_top_tracks(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(token)

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    # Extract track names
    return [track["name"] for track in data["tracks"]]