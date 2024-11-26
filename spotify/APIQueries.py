import requests

def get_auth_header(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers

def artist_search(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=1"

    response = requests.get(url, headers=headers, params=query)
    response.raise_for_status()

    return response.json()