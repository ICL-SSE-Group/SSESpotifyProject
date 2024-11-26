from flask import Flask, render_template, request, jsonify, render_template, redirect, url_for
import os
import requests

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def query():
    spotify_artist = request.form.get("spotify_artist")
    return f"You entered: {spotify_artist}"


if __name__ == "__main__":
    app.debug = True
    app.run()


# Spotify API token from environment
SPOTIFY_TOKEN = os.getenv("SPOTIFY_OAUTH_TOKEN")
if not SPOTIFY_TOKEN:
    raise ValueError("Spotify OAuth token is missing! Ensure it's set in your environment variables.")

def get_auth_header():
    """Generate authorization header."""
    return {
        "Authorization": f"Bearer {SPOTIFY_TOKEN}"
    }

def artist_search(artist_name):
    """Search for an artist by name and return their ID and name."""
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header()
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    if data["artists"]["items"]:
        artist = data["artists"]["items"][0]
        return artist["id"], artist["name"]
    return None, None

def get_artist_top_tracks(artist_id):
    """Fetch the top tracks for the given artist."""
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header()
    params = {"market": "US"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return [track["name"] for track in data["tracks"]]

@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    """Handle the form submission and fetch artist top tracks."""
    artist_name = request.form.get("spotify_artist")
    if not artist_name:
        return redirect(url_for('index'))  # Redirect back to home if no input

    try:
        # Get artist ID
        artist_id, artist_display_name = artist_search(artist_name)
        if not artist_id:
            return render_template("index.html", error="Artist not found. Please try again!")

        # Get top tracks
        top_tracks = get_artist_top_tracks(artist_id)

        # Pass data to the HTML for rendering
        return render_template("index.html", artist_name=artist_display_name, top_tracks=top_tracks)

    except requests.exceptions.RequestException as e:
        return render_template("index.html", error=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)

