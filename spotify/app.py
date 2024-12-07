from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    session,
    url_for,
)
import os
import random
from dotenv import load_dotenv
import sqlite3
from spotify.APIQueries import (
    get_token,
    artist_search,
    get_top_tracks,
    get_tracks_by_album
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

# Flag to ensure reset happens only once
first_request_handled = False


@app.before_request
def reset_on_first_request():
    """Reset tables and session data on the first request."""
    global first_request_handled
    if not first_request_handled:
        try:
            print("Resetting tables on first request...", flush=True)
            reset_tables()
            session.clear()
            first_request_handled = True
            print("Tables and session reset successfully!", flush=True)
        except Exception as e:
            print(f"Error during first request reset: {e}", flush=True)


@app.route("/")
def index():
    """Render the homepage and reset the database tables."""
    try:
        # Reset the database tables
        reset_tables()
        print("Database reset on returning to index.html.", flush=True)

        return render_template("index.html")
    except Exception as e:
        print(f"Error resetting database: {e}", flush=True)
        return render_template("index.html", error=f"Error: {e}")


@app.route("/query", methods=["POST"])
def query():
    """Handle artist queries and display their top tracks."""
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

    artists_top_tracks = {}

    try:
        for artist_index, artist_name in enumerate(artist_names):
            artist_id, artist_display_name = artist_search(
                SPOTIFY_TOKEN, artist_name)
            if not artist_id:
                artists_top_tracks[artist_name] = [
                    {"track": "Artist not found.", "id": artist_index},
                ]
            else:
                top_tracks = get_top_tracks(SPOTIFY_TOKEN, artist_id)
                insert_all_songs(
                    [
                        {
                            "id": f"{artist_index}-{i}",
                            "track": track["track"],
                            "artist": artist_display_name,
                            "album": track["album"],
                            "popularity": track["popularity"],
                            "album_id": track["album_id"]
                        }
                        for i, track in enumerate(top_tracks)
                    ]
                )
                artists_top_tracks[artist_display_name] = [
                    {
                        "track": track["track"],
                        "album": track["album"],
                        "popularity": track["popularity"],
                        "id": f"{artist_index}-{i}",
                        "artist": artist_display_name,
                        "album_id": track["album_id"]
                    }
                    for i, track in enumerate(top_tracks)
                ]
        session["artists_top_tracks"] = artists_top_tracks
        return render_template(
            "return.html", artists_top_tracks=artists_top_tracks)
    except Exception as e:
        return render_template(
            "index.html",
            error=f"An error occurred: {str(e)}",
        )


import random

@app.route("/save_tracks", methods=["POST"])
def save_tracks():
    """Save selected tracks and merge them with all songs."""
    try:
        session.clear()

        selected_tracks = request.json.get("selectedTracks")
        if not selected_tracks:
            return jsonify({
                "status": "error", "message": "No tracks selected"}), 400

        # List to hold tracks fetched from albums
        recommendation_tracks = []

        # Extract album IDs from selected tracks and get album tracks
        for track in selected_tracks:
            album_id = track.get("album_id")
            album_name = track.get("album")
            artist_name = track.get("artist")
            if album_id:
                # Call the function to get tracks by album_id
                album_tracks = get_tracks_by_album(SPOTIFY_TOKEN, album_id)

                # Check if album_tracks is populated
                if album_tracks:
                    print(f"Album Tracks: {album_tracks}")

                    # Randomly select 3 tracks from the album
                    random_tracks = random.sample(album_tracks, 3) if len(album_tracks) >= 3 else album_tracks
                    print(f"Random Tracks: {random_tracks}")

                    # Add the corresponding artist and album to each track
                    for track in random_tracks:
                        track['artist'] = artist_name  # Adding artist to the track
                        track['album'] = album_name    # Adding album name to the track
                        recommendation_tracks.append(track)
                else:
                    print(f"No tracks found for album ID: {album_id}")

        if not recommendation_tracks:
            return jsonify({
                "status": "error", "message": "No album tracks available"}), 400

        # Optionally: Insert the selected tracks into the database
        insert_selected_songs(selected_tracks)
        merge_tables()

        # Store album_tracks in session for access later
        session['recommendation_tracks'] = recommendation_tracks

        # Return success response
        response_data = {
            "status": "success",
            "message": "Tracks saved and merged successfully!",
            "recommendation_tracks": recommendation_tracks  # Return album tracks for debugging or use
        }
        return jsonify(response_data)

    except Exception as e:
        print(f"Error in save_tracks: {e}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500








@app.route("/ranking")
def ranking():
    """Render the ranking page with merged song data."""
    try:
        # Get merged songs from the database
        conn = sqlite3.connect("spotify.db")
        cursor = conn.cursor()
        cursor.execute(
            """SELECT track_name, artist_name, album_name,
            popularity FROM merged_songs"""
        )
        merged_songs = cursor.fetchall()
        conn.close()

        if not merged_songs:
            return redirect(url_for("index"))

        # Get album tracks from session
        recommendation_tracks = session.get('recommendation_tracks', [])

        # Render ranking.html and pass album_tracks to it
        return render_template("ranking.html", merged_songs=merged_songs, recommendation_tracks=recommendation_tracks)
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for("index"))





@app.route("/reset", methods=["POST"])
def reset():
    """Reset all tables and clear session data."""
    try:
        reset_tables()
        session.clear()
        print("Session cleared.", flush=True)
        return jsonify({
            "status": "success", "message": "All tables and sessions reset!"})
    except Exception as e:
        print(f"Reset failed: {e}", flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
