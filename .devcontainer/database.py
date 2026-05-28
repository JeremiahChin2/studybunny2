import sqlite3
import hashlib

DB_FILE = "users.db"

def init_db():
    """Creates the database tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    """Hashes passwords so they aren't stored in plain text."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    """Registers a new user. Returns False if username exists."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    """Checks credentials. Returns user data dict if correct, else None."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT level, exp FROM users WHERE username = ? AND password = ?", 
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    if user:
        return {"level": user[0], "exp": user[1]}
    return None

def save_user_progress(username, level, exp):
    """Saves the bunny stats for a logged-in user."""
    if username == "Guest":
        return # Don't save guest data to the database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET level = ?, exp = ? WHERE username = ?", (level, exp, username))
    conn.commit()
    conn.close()
