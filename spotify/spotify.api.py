import requests
import tkinter as tk
from tkinter import messagebox

# Spotify API credentials
SPOTIFY_TOKEN = "your_spotify_oauth_token_here"

def get_auth_header(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers

def artist_search(artist_name):
    """Fetch artist ID by name."""
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(SPOTIFY_TOKEN)
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    if data["artists"]["items"]:
        return data["artists"]["items"][0]["id"], data["artists"]["items"][0]["name"]
    else:
        return None, None

def get_artist_top_tracks(artist_id):
    """Fetch the top tracks for the given artist."""
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = get_auth_header(SPOTIFY_TOKEN)
    params = {
        "market": "US"  # Specify the market
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return [track["name"] for track in data["tracks"]]

def show_top_tracks():
    """Callback for the Search button."""
    artist_name = artist_name_entry.get().strip()
    if not artist_name:
        messagebox.showwarning("Input Error", "Please enter an artist's name!")
        return

    try:
        artist_id, artist_display_name = artist_search(artist_name)
        if not artist_id:
            messagebox.showerror("Error", "Artist not found!")
            return

        top_tracks = get_artist_top_tracks(artist_id)

        # Open a new window to display top tracks
        top_tracks_window = tk.Toplevel()
        top_tracks_window.title(f"Top Tracks for {artist_display_name}")
        tk.Label(top_tracks_window, text=f"Top Tracks for {artist_display_name}", font=("Arial", 16, "bold")).pack(pady=10)

        for idx, track in enumerate(top_tracks, start=1):
            tk.Label(top_tracks_window, text=f"{idx}. {track}", font=("Arial", 12)).pack(anchor="w", padx=20)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")

# GUI setup
root = tk.Tk()
root.title("Spotify Artist Search")

tk.Label(root, text="Enter Artist Name:", font=("Arial", 14)).pack(pady=10)
artist_name_entry = tk.Entry(root, font=("Arial", 14), width=30)
artist_name_entry.pack(pady=5)

search_button = tk.Button(root, text="Search Top Tracks", font=("Arial", 14), command=show_top_tracks)
search_button.pack(pady=10)

# Run the Tkinter main loop
root.mainloop()
