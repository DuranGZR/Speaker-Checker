import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """
    Creates and returns a new connection to the PostgreSQL database.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "speaker_checker"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        cursor_factory=RealDictCursor
    )

def init_db():
    """
    Initializes the database by creating the required extension, table, and index.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Enable the pg_trgm extension for fast ILIKE/trigram searches.
            # This requires superuser privileges. If it fails, we warn but continue.
            try:
                cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            except Exception as ext_err:
                print(f"Warning: Could not create pg_trgm extension: {ext_err}")
                # Rollback current transaction to keep the connection usable
                conn.rollback()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS youtube_live_videos (
                    id SERIAL PRIMARY KEY,
                    youtube_video_id VARCHAR(100) UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    raw_text TEXT,
                    normalized_raw_text TEXT,
                    video_url TEXT NOT NULL,
                    thumbnail_url TEXT,
                    published_at TIMESTAMP,
                    actual_start_time TIMESTAMP,
                    actual_end_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Try to create the GIN index if pg_trgm was successfully enabled
            try:
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_live_videos_normalized_raw_text_trgm
                    ON youtube_live_videos
                    USING gin (normalized_raw_text gin_trgm_ops);
                """)
            except Exception as idx_err:
                print(f"Warning: Could not create GIN trigram index: {idx_err}")
                conn.rollback()

        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def upsert_live_video(video: dict):
    """
    Inserts a live video record, or updates it if the video ID already exists.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO youtube_live_videos (
                    youtube_video_id,
                    title,
                    description,
                    raw_text,
                    normalized_raw_text,
                    video_url,
                    thumbnail_url,
                    published_at,
                    actual_start_time,
                    actual_end_time
                )
                VALUES (
                    %(youtube_video_id)s,
                    %(title)s,
                    %(description)s,
                    %(raw_text)s,
                    %(normalized_raw_text)s,
                    %(video_url)s,
                    %(thumbnail_url)s,
                    %(published_at)s,
                    %(actual_start_time)s,
                    %(actual_end_time)s
                )
                ON CONFLICT (youtube_video_id)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    raw_text = EXCLUDED.raw_text,
                    normalized_raw_text = EXCLUDED.normalized_raw_text,
                    video_url = EXCLUDED.video_url,
                    thumbnail_url = EXCLUDED.thumbnail_url,
                    published_at = EXCLUDED.published_at,
                    actual_start_time = EXCLUDED.actual_start_time,
                    actual_end_time = EXCLUDED.actual_end_time,
                    updated_at = CURRENT_TIMESTAMP;
            """, video)
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def search_videos_by_name(normalized_name: str):
    """
    Searches for videos where normalized_raw_text contains the normalized_name.
    Ordered by start time descending (most recent first).
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM youtube_live_videos
                WHERE normalized_raw_text ILIKE %s
                ORDER BY actual_start_time DESC NULLS LAST;
            """, (f"%{normalized_name}%",))
            return cur.fetchall()
    finally:
        if conn:
            conn.close()

def count_live_videos():
    """
    Returns the total number of live videos in the database.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS count FROM youtube_live_videos;")
            row = cur.fetchone()
            return row["count"] if row else 0
    except Exception:
        return 0
    finally:
        if conn:
            conn.close()
