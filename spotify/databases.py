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
        popularity INTEGER NOT NULL
    );
    """)

    # Create selected_songs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS selected_songs (
        id TEXT PRIMARY KEY,
        track_name TEXT NOT NULL,
        artist_name TEXT NOT NULL
    );
    """)

    # Optionally create merged_songs table (can be recreated dynamically)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS merged_songs (
        id TEXT PRIMARY KEY,
        track_name TEXT NOT NULL,
        artist_name TEXT NOT NULL,
        album_name TEXT NOT NULL,
        popularity INTEGER NOT NULL
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
                id, track_name, artist_name, album_name, popularity
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                song["id"],
                song["track"],
                song["artist"],
                song["album"],
                song["popularity"],
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
                id, track_name, artist_name
            ) VALUES (?, ?, ?)
            """,
            (song["id"], song["track"], song["artist"]),
        )

    conn.commit()
    print(
        "After insertion, selected_songs:",
        cursor.execute("SELECT * FROM selected_songs").fetchall(),
        flush=True,
    )
    conn.close()


def merge_tables():
    conn = sqlite3.connect("spotify.db")
    cursor = conn.cursor()

    # Clear merged_songs
    cursor.execute("DELETE FROM merged_songs;")
    print("merged_songs table cleared.", flush=True)

    # Insert merged data, ordered by popularity (descending)
    cursor.execute(
        """
        INSERT INTO merged_songs (
            id, track_name, artist_name, album_name, popularity
        )
        SELECT
            s.id,
            s.track_name,
            s.artist_name,
            a.album_name,
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
    print(
        "Merged songs table updated and sorted by popularity successfully.",
        flush=True)


def reset_tables():
    conn = sqlite3.connect("spotify.db")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM merged_songs;")
        print("merged_songs table cleared.", flush=True)
        cursor.execute("DELETE FROM selected_songs;")
        print("selected_songs table cleared.", flush=True)
        cursor.execute("DELETE FROM all_songs;")
        print("all_songs table cleared.", flush=True)

        conn.commit()
    except Exception as e:
        print(f"Error in reset_tables: {e}", flush=True)
    finally:
        conn.close()
        print("Database connection closed.", flush=True)
