from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
)
from dotenv import load_dotenv
import os
import random
import sqlite3
from spotify.APIQueries import (
    get_token,
    artist_search,
    get_top_tracks,
    get_tracks_by_album,
)
from spotify.databases import (
    init_db,
    insert_all_songs,
    insert_selected_songs,
    merge_tables,
    reset_tables,
)

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
    """Render the homepage and reset the database tables."""
    try:
        reset_tables()
        return render_template("index.html")

    except Exception as e:
        print(f"Error resetting database: {e}", flush=True)
        return render_template("index.html", error=f"Error: {e}")


@app.route("/query", methods=["POST"])
def query():
    """Handle artist queries and display their top tracks."""

    # Extract artist names from form submission
    artist_names = [
        request.form.get("spotify_artist1"),
        request.form.get("spotify_artist2"),
        request.form.get("spotify_artist3"),
    ]
    artist_names = [name for name in artist_names if name]

    if not artist_names:
        return render_template(
            "index.html",
            error="Please enter at least one artist name!",
        )

    # Dictionary to store top tracks for each artist
    artists_top_tracks = {}

    try:
        # Search for each artist and get their Spotify ID and display name
        for artist_index, artist_name in enumerate(artist_names):
            artist_id, artist_display_name = artist_search(
                SPOTIFY_TOKEN, artist_name
            )

            if not artist_id:
                artists_top_tracks[artist_name] = [
                    {"track": "Artist not found.", "id": artist_index},
                ]

            # Fetch artist's top tracks using their Spotify ID
            else:
                top_tracks = get_top_tracks(SPOTIFY_TOKEN, artist_id)

                # Insert all top tracks into the database
                insert_all_songs(
                    [
                        {
                            "id": f"{artist_index}-{i}",
                            "track": track["track"],
                            "artist": artist_display_name,
                            "album": track["album"],
                            "popularity": track["popularity"],
                            "album_id": track["album_id"],
                            "release_date": track["release_date"],
                        }
                        for i, track in enumerate(top_tracks)
                    ]
                )
                # Format and store the top tracks for rendering in the response
                artists_top_tracks[artist_display_name] = [
                    {
                        "track": track["track"],
                        "album": track["album"],
                        "popularity": track["popularity"],
                        "id": f"{artist_index}-{i}",
                        "artist": artist_display_name,
                        "album_id": track["album_id"],
                        "release_date": track["release_date"],
                    }
                    for i, track in enumerate(top_tracks)
                ]

        # Render the results page with the top tracks for each artist
        return render_template("return.html",
                               artists_top_tracks=artists_top_tracks)

    except Exception as e:
        return render_template(
            "index.html",
            error=f"An error occurred: {str(e)}",
        )


@app.route("/save_tracks", methods=["POST"])
def save_tracks():
    """Save selected tracks and merge them with all songs."""
    try:
        # Get the selected tracks from the request JSON payload
        selected_tracks = request.json.get("selectedTracks")

        if not selected_tracks:
            return jsonify({
                "status": "error",
                "message": "No tracks selected",
            }), 400

        # Insert selected tracks into the database
        insert_selected_songs(selected_tracks)
        # SQL JOIN with all songs database
        merge_tables()

        # Connect to the database for inserting recommendations
        conn = sqlite3.connect("spotify.db")
        cursor = conn.cursor()

        for track in selected_tracks:
            album_id = track.get("album_id")
            album_name = track.get("album_name")
            artist_name = track.get("artist")
            if album_id:
                # Fetch tracks from the album using its Spotify ID
                album_tracks = get_tracks_by_album(SPOTIFY_TOKEN, album_id)

                # Randomly select up to 3 tracks from the album
                if album_tracks:
                    random_tracks = random.sample(
                        album_tracks, 3
                    ) if len(album_tracks) >= 3 else album_tracks

                    for random_track in random_tracks:
                        # Insert the recommended track into the database
                        cursor.execute("""
                            INSERT OR IGNORE INTO recommended_songs (
                                id,
                                track_name,
                                artist_name,
                                album_name,
                                album_id
                            ) VALUES (?, ?, ?, ?, ?)
                        """, (
                            random_track.get("id"),
                            random_track.get("track"),
                            artist_name,
                            album_name,
                            album_id
                        ))

        # Commit and close the database connection
        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Tracks saved and merged successfully!"
        })

    except Exception as e:
        print(f"Error in save_tracks: {e}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/ranking")
def ranking():
    """Render the ranking page with merged song data and recommendations."""
    try:
        conn = sqlite3.connect("spotify.db")
        cursor = conn.cursor()

        # Fetch merged songs for ranking
        cursor.execute("""
            SELECT track_name,
            artist_name,
            album_name,
            release_date,
            popularity
            FROM merged_songs
        """)
        merged_songs = cursor.fetchall()

        # Fetch recommended songs from the database
        cursor.execute("""
            SELECT track_name, artist_name, album_name
            FROM recommended_songs
        """)
        recommended_songs = cursor.fetchall()

        conn.close()

        if not merged_songs:
            return redirect(url_for("index"))

        # Render the ranking page with merged songs and recommendations
        return render_template(
            "ranking.html",
            merged_songs=merged_songs,
            recommendation_tracks=recommended_songs,
        )

    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset():
    """Reset all tables and clear session data."""
    try:
        # Clear all database tables
        reset_tables()

        return jsonify({
            "status": "success",
            "message": "All tables and sessions reset!",
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
