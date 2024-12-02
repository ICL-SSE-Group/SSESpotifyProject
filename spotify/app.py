from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from APIQueries import get_token, artist_search, get_top_tracks

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Fetch the Spotify token
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
if not client_id or not client_secret:
    raise ValueError("CLIENT_ID or CLIENT_SECRET is missing from .env!")
SPOTIFY_TOKEN = get_token(client_id, client_secret)

@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    artist_name = request.form.get("spotify_artist")
    print(f"Received artist name: {artist_name}")  # Debugging log

    if not artist_name:
        print("Artist name is missing.")  # Debugging log
        return render_template("index.html", error="Please enter an artist name!")

    try:
        print("Fetching artist data...")  # Debugging log
        # Get artist ID and display name
        artist_id, artist_display_name = artist_search(SPOTIFY_TOKEN, artist_name)
        print(f"Artist ID: {artist_id}, Artist Name: {artist_display_name}")  # Debugging log

        if not artist_id:
            print("Artist not found.")  # Debugging log
            return render_template("index.html", error="Artist not found. Please try again!")

        print("Fetching top tracks...")  # Debugging log
        # Get top tracks
        top_tracks = get_top_tracks(SPOTIFY_TOKEN, artist_id)
        print(f"Top Tracks: {top_tracks}")  # Debugging log

        print("Rendering return.html template...")  # Debugging log
        # Render the return.html template with data
        return render_template(
            "return.html",
            artist_name=artist_display_name,
            top_tracks=top_tracks,
        )

    except Exception as e:
        print(f"Error occurred: {e}")  # Log the error
        return render_template("index.html", error=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
