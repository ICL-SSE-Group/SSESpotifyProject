from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from APIQueries import get_token, artist_search, get_top_tracks #, audio_features

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
        return render_template("index.html", error="Please enter at least one artist name!")

    artists_top_tracks = {}  # Dictionary to hold artist names and their top tracks
    track_id_counter = 0  # Initialize a counter for unique track IDs

    try:
        # Loop through each artist's name to fetch data
        for artist_index, artist_name in enumerate(artist_names):
            print(f"Fetching data for: {artist_name}")  # Debugging
            artist_id, artist_display_name = artist_search(SPOTIFY_TOKEN, artist_name)

            if not artist_id:
                print(f"Artist not found: {artist_name}")  # Debugging
                artists_top_tracks[artist_name] = [{"track": "Artist not found.", "id": track_id_counter}]
                track_id_counter += 1
            else:
                # Get top tracks for the artist
                top_tracks = get_top_tracks(SPOTIFY_TOKEN, artist_id)
                
                # Create the list of top tracks with unique IDs for each track
                artists_top_tracks[artist_display_name] = [
                    {"track": track, "id": f"{artist_index}-{i}"} for i, track in enumerate(top_tracks)
                ]
                track_id_counter += len(top_tracks)

        print(f"Artists and their top tracks: {artists_top_tracks}")  # Debugging
        return render_template("return.html", artists_top_tracks=artists_top_tracks)

    except Exception as e:
        print(f"Error occurred: {e}")  # Debugging log
        return render_template("index.html", error=f"An error occurred: {str(e)}")




#@app.route("/track-features", methods=["GET"])
#def track_features():
    #track_id = request.form.get("track_id")

    #token = APIQueries.get_token(CLIENT_ID, CLIENT_SECRET)
    
    #try:
        #features = APIQueries.get_audio_features(token, track_id)
    #except requests.exceptions.RequestException as e:
        #return f"Error fetching audio features: {e}", 500

    #return render_template("party-ometer.html", features=features)











if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
