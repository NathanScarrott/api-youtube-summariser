import sqlite3
from typing import List, Tuple, Optional


def get_connection(db_name: str) -> sqlite3.Connection:
    """Create and return a database connection."""
    try:
        return sqlite3.connect(db_name)
    except Exception as e:
        print(f"Database connection error: {e}")
        raise


def create_table(connection: sqlite3.Connection) -> None:
    """Create the summaries table if it doesn't exist."""
    query = """
    CREATE TABLE IF NOT EXISTS summaries (
        id INTEGER PRIMARY KEY,
        summary TEXT,
        videoId TEXT NOT NULL,
        playlistId TEXT,
        transcript TEXT
    )
    """
    
    try:
        with connection:
            connection.execute(query)
    except Exception as e:
        print(f"Error creating table: {e}")
        raise


def create_favourites_table(connection: sqlite3.Connection) -> None:
    """Create the favourites table if it doesn't exist."""
    query = """
    CREATE TABLE IF NOT EXISTS favourites (
        id INTEGER PRIMARY KEY,
        videoId TEXT NOT NULL,
        summary TEXT
    )
    """
    
    try:
        with connection:
            connection.execute(query)
    except Exception as e:
        print(f"Error creating favourites table: {e}")
        raise


def insert_summary(connection: sqlite3.Connection, summary: str, video_id: str, playlist_id: Optional[str] = None) -> None:
    """Insert a summary into the database."""
    query = "INSERT INTO summaries (summary, videoId, playlistId) VALUES (?, ?, ?)"
    try:
        with connection:
            connection.execute(query, (summary, video_id, playlist_id))
    except Exception as e:
        print(f"Error inserting summary: {e}")
        raise


def insert_transcript(connection: sqlite3.Connection, transcript: str, video_id: str, playlist_id: Optional[str] = None) -> None:
    """Insert a transcript into the database."""
    query = "INSERT INTO summaries (transcript, videoId, playlistId) VALUES (?, ?, ?)"
    try:
        with connection:
            connection.execute(query, (transcript, video_id, playlist_id))
    except Exception as e:
        print(f"Error inserting transcript: {e}")
        raise


def insert_favourite(connection: sqlite3.Connection, video_id: str, summary: str) -> None:
    """Insert a favourite into the database."""
    query = "INSERT INTO favourites (videoId, summary) VALUES (?, ?)"
    try:
        with connection:
            connection.execute(query, (video_id, summary))
    except Exception as e:
        print(f"Error inserting favourite: {e}")
        raise


def fetch_data_by_video_id(connection: sqlite3.Connection, video_id: str) -> List[Tuple]:
    """Fetch data for a specific video ID."""
    query = "SELECT * FROM summaries WHERE videoId = ?"
    try:
        with connection:
            rows = connection.execute(query, (video_id,)).fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching data for video {video_id}: {e}")
        return []


def fetch_all_summaries(connection: sqlite3.Connection) -> List[Tuple]:
    """Fetch all summaries from the database."""
    query = "SELECT * FROM summaries"
    try:
        with connection:
            rows = connection.execute(query).fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching summaries: {e}")
        return []


def fetch_all_favourites(connection: sqlite3.Connection) -> List[Tuple]:
    """Fetch all favourites from the database."""
    query = "SELECT * FROM favourites"
    try:
        with connection:
            rows = connection.execute(query).fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching favourites: {e}")
        return []