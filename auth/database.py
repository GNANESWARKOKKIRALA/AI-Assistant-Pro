"""
auth/database.py — SQLite database setup for user authentication
"""
import sqlite3
import os
from typing import Optional, Dict

USERS_DB_PATH = os.path.join("database", "users.db")


def get_connection() -> sqlite3.Connection:
    """Return a connection to the users database."""
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(USERS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_users_db() -> None:
    """Create users table if it doesn't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            email      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def create_user(name: str, email: str, password_hash: str) -> bool:
    """
    Insert a new user. Returns True on success, False if email already exists.
    """
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name.strip(), email.strip().lower(), password_hash)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # email already exists


def get_user_by_email(email: str) -> Optional[Dict]:
    """Fetch user row by email. Returns dict or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email.strip().lower(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Fetch user row by id. Returns dict or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None
