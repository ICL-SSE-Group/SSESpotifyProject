from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from spotify.APIQueries import get_token, artist_search, get_top_tracks  # , audio_features
from spotify.databases import init_db, insert_song, fetch_all_songs

# Initialize Flask app - This should be the first line after imports
app = Flask(__name__)  # Make sure this is defined before any routes!

# Load environment variables
load_dotenv()

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
    """Handle artist queries and display their top tracks."""
    print("Query route triggered!")  # Debugging

    # Get artist names from form inputs
    artist_names = [
        request.form.get("spotify_artist1"),
        request.form.get("spotify_artist2"),
        request.form.get("spotify_artist3"),
    ]
    print(f"Received artist names: {artist_names}")  # Debugging

    # Filter out any empty inputs
    artist_names = [name for name in artist_names if name]
    if not artist_names:
        print("No artist names provided!")  # Debugging
        return render_template(
            "index.html", error="Please enter at least one artist name!"
        )

    artists_top_tracks = {}  # Dictionary to hold artist names and their top tracks
    track_id_counter = 0  # Initialize a counter for unique track IDs

    try:
        # Loop through each artist's name to fetch data
        for artist_index, artist_name in enumerate(artist_names):
            print(f"Fetching data for: {artist_name}")  # Debugging
            artist_id, artist_display_name = artist_search(SPOTIFY_TOKEN, artist_name)

            if not artist_id:
                print(f"Artist not found: {artist_name}")  # Debugging
                artists_top_tracks[artist_name] = [
                    {"track": "Artist not found.", "id": track_id_counter}
                ]
                track_id_counter += 1
            else:
                # Get top tracks for the artist
                top_tracks = get_top_tracks(SPOTIFY_TOKEN, artist_id)

                # Create the list of top tracks with unique IDs for each track
                artists_top_tracks[artist_display_name] = [
                    {"track": track, "id": f"{artist_index}-{i}"}
                    for i, track in enumerate(top_tracks)
                ]
                track_id_counter += len(top_tracks)

        print(f"Artists and their top tracks: {artists_top_tracks}")  # Debugging
        return render_template("return.html", artists_top_tracks=artists_top_tracks)

    except Exception as e:
        print(f"Error occurred: {e}")  # Debugging log
        return render_template("index.html", error=f"An error occurred: {str(e)}")
    
@app.route("/save_tracks", methods=["POST"])
def save_tracks():
    data = request.get_json()
    if not data or not data.get('selectedTracks'):
        return jsonify({"error": "No tracks provided"}), 400

    for track in data['selectedTracks']:
        song_id = track['id']
        song_name = track['name']
        artist_name = track['artist']
        danceability = get_danceability(SPOTIFY_TOKEN, song_id)  # Fetch from Spotify API

        # Save to database
        insert_song(song_id, song_name, artist_name, danceability)

        return jsonify({"message": "Tracks saved successfully!"})


@app.route("/ranking")
def view_playlist():
    playlist = fetch_all_songs()
    # Sort playlist by danceability
    sorted_playlist = sorted(playlist, key=lambda song: song['danceability'], reverse=True)
    return render_template("ranking.html", playlist=sorted_playlist)


if __name__ == "__main__":
    init_db()
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
