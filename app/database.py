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
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO userdata (email, password)
        VALUES (?, ?)
        """, (email, password))
    conn.commit()
    conn.close()
    

def get_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, password
        FROM userdata 
        WHERE email = ?
        """, (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_test_user():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO userdata (email, password)
        VALUES (?, ?)
        """, ("user1@test.com", "user123")
    )
    conn.commit()
    conn.close()