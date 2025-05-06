import sqlite3

def init_db():
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            last_message TEXT,
            last_response TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_message(phone, message, response):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO clients (phone, last_message, last_response) VALUES (?, ?, ?)",
              (phone, message, response))
    conn.commit()
    conn.close()