
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "bookrec.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reading_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                book_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, book_id)
            )
        """)

def add_to_reading_list(user_id, book_id):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO reading_list (user_id, book_id)
            VALUES (?, ?)
            """,
            (user_id, book_id)
        )

def remove_from_reading_list(user_id, book_id):
    with get_connection() as conn:
        conn.execute(
            """
            DELETE FROM reading_list
            WHERE user_id = ? AND book_id = ?
            """,
            (user_id, book_id)
        )

def get_reading_list(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT book_id
            FROM reading_list
            WHERE user_id = ?
            ORDER BY added_at DESC, id DESC
            """,
            (user_id,)
        ).fetchall()

    return [row[0] for row in rows]
