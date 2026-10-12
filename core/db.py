import sqlite3
import uuid

DB_PATH = "data/app.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize all tables cleanly in one centralized place."""
    conn = get_connection()
    c = conn.cursor()
    
    # Users table (Replacing users.json)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    
    # User progress table
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id TEXT,
            skill TEXT,
            status TEXT,
            PRIMARY KEY (user_id, skill)
        )
    """)
    
    conn.commit()
    conn.close()

# --- User Management Functions ---

def create_user(name, email, password_hash):
    """Insert a new user into SQLite instead of users.json."""
    conn = get_connection()
    c = conn.cursor()
    user_id = str(uuid.uuid4())
    try:
        c.execute("""
            INSERT INTO users (user_id, name, email, password_hash)
            VALUES (?, ?, ?, ?)
        """, (user_id, name, email, password_hash))
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None  # Email already exists
    finally:
        conn.close()

def get_user_by_email(email):
    """Retrieve user details by email for login verification."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

# --- Progress Tracking Functions ---

def save_progress(user_id, skill, status):
    """Save or update user skill progress."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO user_progress (user_id, skill, status)
        VALUES (?, ?, ?)
    """, (user_id, skill, status))
    conn.commit()
    conn.close()

def get_progress(user_id):
    """Retrieve all progress records for a given user."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT skill, status FROM user_progress WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return {row["skill"]: row["status"] for row in rows}