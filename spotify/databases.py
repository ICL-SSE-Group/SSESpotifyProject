import sqlite3

# Initialize the database connection
def init_db():
    connection = sqlite3.connect("spotify.db")
    cursor = connection.cursor()

    # Create the songs table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id TEXT PRIMARY KEY,
            song_name TEXT NOT NULL,
            artist_name TEXT NOT NULL,
            danceability REAL NOT NULL
        )
    """)
    connection.commit()
    connection.close()

# Insert a song into the database
def insert_song(song_id, song_name, artist_name, danceability):
    connection = sqlite3.connect("spotify.db")
    cursor = connection.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO songs (id, song_name, artist_name, danceability)
        VALUES (?, ?, ?, ?)
    """, (song_id, song_name, artist_name, danceability))

    connection.commit()
    connection.close()

# Fetch all songs from the database
def fetch_all_songs():
    connection = sqlite3.connect("spotify.db")
    cursor = connection.cursor()
    
    cursor.execute("SELECT * FROM songs")
    rows = cursor.fetchall()
    
    connection.close()
    return rows
