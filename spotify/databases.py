import sqlite3


def init_db():
    from sqlite3 import connect

    conn = connect("spotify.db")
    cursor = conn.cursor()

    # Create all_songs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS all_songs (
        id TEXT PRIMARY KEY,
        track_name TEXT NOT NULL,
        artist_name TEXT NOT NULL,
        album_name TEXT NOT NULL,
        popularity INTEGER NOT NULL,
        album_id TEXT NOT NULL,
        release_date TEXT NOT NULL
    );
    """)

    # Create selected_songs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS selected_songs (
        id TEXT PRIMARY KEY,
        track_name TEXT NOT NULL,
        artist_name TEXT NOT NULL,
        album_name TEXT NOT NULL,
        album_id TEXT NOT NULL
    );
    """)

    # Optionally create merged_songs table (can be recreated dynamically)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS merged_songs (
        id TEXT PRIMARY KEY,
        track_name TEXT NOT NULL,
        artist_name TEXT NOT NULL,
        album_name TEXT NOT NULL,
        release_date TEXT NOT NULL,
        popularity INTEGER NOT NULL
    );
    """)

    # Create recommended_songs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommended_songs (
        id TEXT PRIMARY KEY,
        track_name TEXT NOT NULL,
        artist_name TEXT NOT NULL,
        album_name TEXT NOT NULL,
        album_id TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()


def insert_all_songs(songs):
    conn = sqlite3.connect("spotify.db")
    cursor = conn.cursor()
    for song in songs:
        cursor.execute(
            """
            INSERT OR IGNORE INTO all_songs (
                id, track_name, artist_name, album_name,
                popularity, album_id, release_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                song["id"],
                song["track"],
                song["artist"],
                song["album"],
                song["popularity"],
                song["album_id"],
                song["release_date"]
            ),
        )
    conn.commit()
    conn.close()


def insert_selected_songs(selected_songs):
    conn = sqlite3.connect("spotify.db")
    cursor = conn.cursor()

    for song in selected_songs:
        cursor.execute(
            """
            INSERT OR REPLACE INTO selected_songs (
                id, track_name, artist_name, album_name, album_id
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (song["id"], song["track"], song["artist"],
             song["album_name"], song["album_id"])
        )

    conn.commit()
    conn.close()


def merge_tables():
    conn = sqlite3.connect("spotify.db")
    cursor = conn.cursor()

    # Clear merged_songs
    cursor.execute("DELETE FROM merged_songs;")

    # Insert merged data, ordered by popularity (descending)
    cursor.execute(
        """
        INSERT INTO merged_songs (
            id, track_name, artist_name, album_name, release_date, popularity
        )
        SELECT
            s.id,
            s.track_name,
            s.artist_name,
            s.album_name,
            a.release_date,
            a.popularity
        FROM
            selected_songs s
        JOIN
            all_songs a
        ON
            s.id = a.id
        ORDER BY a.popularity DESC;
        """
    )

    conn.commit()
    conn.close()


def reset_tables():
    """Clear all tables and ensure proper closure of the connection."""
    try:
        conn = sqlite3.connect("spotify.db")
        cursor = conn.cursor()

        # List of tables to be cleared
        tables = ["merged_songs",
                  "selected_songs",
                  "all_songs",
                  "recommended_songs"]

        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table};")
            except sqlite3.OperationalError:
                print(
                    f"Table {table} does not exist or could not be cleared.",
                    flush=True)

        conn.commit()

    except Exception as e:
        print(f"Error in reset_tables: {e}", flush=True)
    finally:
        if conn:
            conn.close()
