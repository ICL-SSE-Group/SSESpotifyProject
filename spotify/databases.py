import sqlite3

# Database file name
DB_FILE = "spotify.db"

# Initialize the database connection and create the songs table
def init_db():
    """Initialize the database and create the 'songs' table if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id TEXT PRIMARY KEY,            -- Unique song ID (can be a Spotify track ID)
                song_name TEXT NOT NULL,        -- Name of the song
                artist_name TEXT NOT NULL,      -- Name of the artist
                danceability REAL NOT NULL      -- Danceability score (a float between 0 and 1)
            )
        """)
        connection.commit()

# Insert or update a song in the database
def insert_song(song_id, song_name, artist_name, danceability):
    """Insert or update a song in the 'songs' table."""
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO songs (id, song_name, artist_name, danceability)
            VALUES (?, ?, ?, ?)
        """, (song_id, song_name, artist_name, danceability))
        connection.commit()

# Fetch all songs from the database
def fetch_all_songs():
    """Fetch all songs from the 'songs' table."""
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, song_name, artist_name, danceability FROM songs")
        rows = cursor.fetchall()
        
    # Convert rows (list of tuples) into a list of dictionaries for better readability
    songs = [
        {"id": row[0], "song_name": row[1], "artist_name": row[2], "danceability": row[3]}
        for row in rows
    ]
    return songs
