import os
import base64
import requests
#from flask import Flask, render_template, request
#from dotenv import load_dotenv


def get_token(client_id, client_secret):
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode()
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}"
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        print(f"Failed to fetch token: {response.status_code}, {response.text}")
    response.raise_for_status()
    return response.json()["access_token"]


def get_auth_header(token):
    return {
        "Authorization": f"Bearer {token}"
    }


def artist_search(token, artist_name):
    url = "https://api.spotify.com/v1/search"  # Endpoint for search
    headers = get_auth_header(token)  # Create authorization header with access token

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
    params = {"market": "US"}  # Add required parameter
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return [track["name"] for track in data["tracks"]]

def audio_features(token, track_id):
    url = "https://api.spotify.com/v1/audio-features/{id}/danceability"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad HTTP status
    return response.json()

def get_songs_sorted_by_danceability():
    # Example database query using SQLAlchemy or any database library
    from your_database_model import db, Song  # Replace with your database setup
    return Song.query.order_by(Song.danceability.desc()).all()