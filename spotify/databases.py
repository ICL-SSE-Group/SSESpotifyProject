import sqlite3

# Database file name
DB_FILE = "spotify.db"

# Initialize the database connection and create the songs table
def init_db():
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        # Create the songs table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id TEXT PRIMARY KEY,            -- Spotify track ID
                song_name TEXT NOT NULL,        -- Name of the song
                artist_name TEXT NOT NULL,      -- Name of the artist
                album_name TEXT,                -- Name of the album
                popularity INTEGER NOT NULL     -- Popularity score
            )
        """)
        connection.commit()

# Insert or update a song in the database
def insert_song(song_id, song_name, artist_name, album_name, popularity):
    """Insert or update a song in the 'songs' table."""
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO songs (
            id, song_name, artist_name, album_name, popularity)
            VALUES (?, ?, ?, ?, ?)
        """, (song_id, song_name, artist_name, album_name, popularity))
        connection.commit()

# Fetch all songs from the database
def fetch_all_songs():
    """Fetch all songs from the 'songs' table."""
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()
        cursor.execute("""
                       SELECT id, song_name, artist_name, album_name, popularity
                       FROM songs
                       """)
        rows = cursor.fetchall()
        # Return each song as a dictionary
        return [
            {
                "id": row[0],
                "song_name": row[1],
                "artist_name": row[2],
                "album_name": row[3],
                "popularity": row[4]
            }
            for row in rows
        ]
