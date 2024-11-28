import base64
import requests

def get_spotify_token(client_id, client_secret):
    # Spotify's token endpoint
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# Replace these with your actual Client ID and Client Secret
client_id = "9f309a6f71bd4c7fa18ddab47352e7ae"
client_secret = "a0bb0b31dd6f4baab31779cde4601a00"

token = get_spotify_token(client_id, client_secret)
print("Spotify OAuth Token:", token)
