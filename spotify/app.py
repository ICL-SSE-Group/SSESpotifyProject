from flask import Flask, render_template, request, jsonify, redirect
import os
from dotenv import load_dotenv
from spotify.APIQueries import (
    get_token,
    artist_search,
    get_top_tracks,
    get_track_details
)
from spotify.databases import init_db, insert_song, fetch_all_songs

app = Flask(__name__)  # Initialize Flask app

if __name__ == "__main__":
    init_db()  # Initialize database and create tables
    app.debug = True  # Enable debug mode
    app.run(host="0.0.0.0", port=8000)

load_dotenv()

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
            artist_id, artist_display_name = artist_search(SPOTIFY_TOKEN, artist_name)
            if not artist_id:
                artists_top_tracks[artist_name] = [
                    {"track": "Artist not found.", "id": artist_index},
                ]
            else:
                top_tracks = get_top_tracks(SPOTIFY_TOKEN, artist_id)
                artists_top_tracks[artist_display_name] = [
                    {
                        "track": track["track"],
                        "album": track["album"],
                        "id": f"{artist_index}-{i}",
                        "artist": artist_display_name,
                    }
                    for i, track in enumerate(top_tracks)
                ]

        return render_template(
            "return.html", artists_top_tracks=artists_top_tracks
        )
    except Exception as e:
        return render_template(
            "index.html",
            error=f"An error occurred: {str(e)}",
        )


@app.route('/save_tracks', methods=['POST'])
def save_tracks():
    selected_tracks = request.form.get("selectedTracks")
    
    if not selected_tracks:
        return jsonify({'message': 'No tracks selected!'}), 400

    selected_tracks = json.loads(selected_tracks)  # Parse the JSON data

    # You can now process and save the selected tracks
    track_data = []
    for track in selected_tracks:
        # Here you could save the tracks to the database or perform other logic
        track_data.append({
            'id': track['id'],
            'track': track['track'],
            'artist': track['artist'],
            'album': track['album']
        })

    # Return the response with the saved tracks
    return jsonify({'message': 'Tracks saved successfully!', 'data': track_data}), 200


@app.route("/ranking")
def view_playlist():
    """View the playlist ranked by popularity or other stats."""
    playlist = fetch_all_songs()

    # Sort playlist by popularity (or use another stat like 'valence', 'tempo')
    sorted_playlist = sorted(
        playlist, key=lambda song: song["popularity"], reverse=True
    )

    # Render the sorted playlist in the ranking template
    return render_template("ranking.html", playlist=sorted_playlist)
