from datetime import datetime
from app.auth import secure_hash
import sqlite3

DATABASE = "userdata.db"

def get_connection():
    return sqlite3.connect(DATABASE)

def create_user_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS userdata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_user(email, password_hash, created_at):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO userdata (email, password_hash, created_at)
        VALUES (?, ?, ?)
        """, (email, password_hash, created_at))
    conn.commit()
    conn.close()
    

def get_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, password_hash, created_at
        FROM userdata 
        WHERE email = ?
        """, (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_test_user():
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = secure_hash("user123")
    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT OR IGNORE INTO userdata (email, password_hash, created_at)
        VALUES (?, ?, ?)
        """, ("user1@test.com", password_hash, created_at)
    )
    conn.commit()
    conn.close()