from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import os
import sqlite3
from dotenv import load_dotenv
from spotify.APIQueries import (
    get_token,
    artist_search,
    get_top_tracks
)
from spotify.databases import init_db, insert_all_songs, insert_selected_songs, merge_tables, reset_tables

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure Flask secret key
app.secret_key = os.urandom(24)

# Fetch Spotify API credentials
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
if not client_id or not client_secret:
    raise ValueError("CLIENT_ID or CLIENT_SECRET is missing from .env!")

# Fetch Spotify token
SPOTIFY_TOKEN = get_token(client_id, client_secret)

# Initialize database
init_db()


@app.route("/")
def index():
    """Render the homepage."""
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def query():
    """Handle artist queries and display their top tracks."""
    artist_names = [
        request.form.get("spotify_artist1"),
        request.form.get("spotify_artist2"),
        request.form.get("spotify_artist3"),
    ]
    # Filter out any empty artist names
    artist_names = [name for name in artist_names if name]
    if not artist_names:
        return render_template(
            "index.html",
            error="Please enter at least one artist name!",
        )

    artists_top_tracks = {}

    try:
        for artist_index, artist_name in enumerate(artist_names):
            # Search for the artist using the Spotify API
            artist_id, artist_display_name = artist_search(SPOTIFY_TOKEN, artist_name)
            if not artist_id:
                # Handle case where artist is not found
                artists_top_tracks[artist_name] = [
                    {"track": "Artist not found.", "id": artist_index},
                ]
            else:
                # Get the artist's top tracks
                top_tracks = get_top_tracks(SPOTIFY_TOKEN, artist_id)

                # Save top tracks to the database
                insert_all_songs([
                    {
                        "id": f"{artist_index}-{i}",
                        "track": track["track"],
                        "artist": artist_display_name,
                        "album": track["album"],
                        "popularity": track["popularity"]
                    }
                    for i, track in enumerate(top_tracks)
                ])

                # Add the tracks to the dictionary for rendering
                artists_top_tracks[artist_display_name] = [
                    {
                        "track": track["track"],
                        "album": track["album"],
                        "popularity": track["popularity"],
                        "id": f"{artist_index}-{i}",
                        "artist": artist_display_name,
                    }
                    for i, track in enumerate(top_tracks)
                ]

        # Save the data to the session for rendering later
        session["artists_top_tracks"] = artists_top_tracks

        return render_template("return.html", artists_top_tracks=artists_top_tracks)

    except Exception as e:
        return render_template(
            "index.html",
            error=f"An error occurred: {str(e)}",
        )


@app.route("/save_tracks", methods=["POST"])
def save_tracks():
    """Save selected tracks and merge them with all songs."""
    try:
        # Parse the JSON data from the request
        selected_tracks = request.json.get("selectedTracks")
        if not selected_tracks:
            return jsonify({"status": "error", "message": "No tracks selected"}), 400

        # Save the selected tracks into the database
        insert_selected_songs(selected_tracks)

        # Merge the selected tracks with all songs to create the merged_songs table
        merge_tables()

        return jsonify({"status": "success", "message": "Tracks saved and merged successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/ranking")
def ranking():
    """Render the ranking page with merged song data."""
    try:
        # Connect to the database
        conn = sqlite3.connect('spotify.db')
        cursor = conn.cursor()

        # Fetch all tracks from the merged_songs table
        cursor.execute("SELECT track_name, artist_name, album_name, popularity FROM merged_songs")
        merged_songs = cursor.fetchall()
        conn.close()

        # If no tracks are available, redirect to the home page
        if not merged_songs:
            return redirect(url_for('index'))

        # Render the ranking page with the merged songs data
        return render_template("ranking.html", merged_songs=merged_songs)

    except Exception as e:
        # Handle database or other errors gracefully
        print(f"Error: {e}")
        return redirect(url_for('index'))


# Run the application
if __name__ == "__main__":
    reset_tables()
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
