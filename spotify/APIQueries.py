import requests

def get_auth_header(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers


def artist_search(token, artist_name):
    url = "https://api.spotify.com/v1/search" #endpoint for search for item function
    headers = get_auth_header(token) #create authorization header with access token
    query = f"q={artist_name}&type=artist&limit=1"

    response = requests.get(url, headers=headers, params=query)
    response.raise_for_status()
    data = response.json()

    if not data['artists']['items']:
        raise ValueError("Artist not found!")

    artist_id = data['artist']['items'][0]['id']
    return artist_id



def get_top_tracks(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{id}/top-tracks"
    headers = get_auth_header(token)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    tracks_data = response.json()

    # extracts track name
    top_tracks = [{"name": track["name"]} for track in tracks_data['tracks']]
    return top_tracks