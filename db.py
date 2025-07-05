import sqlite3

conn = sqlite3.connect("base.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        user_count INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        server_id INTEGER,
        config_id TEXT,
        config_url TEXT,
        last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (server_id) REFERENCES servers(id)
    )
    """)
    conn.commit()

def add_server(name, url, username, password):
    cursor.execute("INSERT INTO servers (name, url, username, password) VALUES (?, ?, ?, ?)",
                   (name, url, username, password))
    conn.commit()

def get_all_servers():
    cursor.execute("SELECT id, name, user_count FROM servers WHERE user_count < 150")
    return cursor.fetchall()

def get_server_by_id(server_id):
    cursor.execute("SELECT url, username, password FROM servers WHERE id = ?", (server_id,))
    return cursor.fetchone()

def get_available_server():
    cursor.execute("SELECT id, url, username, password FROM servers WHERE user_count < 150 LIMIT 1")
    return cursor.fetchone()

def increment_server_user_count(server_id):
    cursor.execute("UPDATE servers SET user_count = user_count + 1 WHERE id = ?", (server_id,))
    conn.commit()

def decrement_server_user_count(server_id):
    cursor.execute("UPDATE servers SET user_count = user_count - 1 WHERE id = ?", (server_id,))
    conn.commit()

def save_user_config(user_id, server_id, config_id, config_url):
    cursor.execute("INSERT OR REPLACE INTO users (user_id, server_id, config_id, config_url) VALUES (?, ?, ?, ?)",
                   (user_id, server_id, config_id, config_url))
    increment_server_user_count(server_id)
    conn.commit()

def get_server_user_count(server_id):
    cursor.execute("SELECT COUNT(*) FROM users WHERE server_id = ?", (server_id,))
    return cursor.fetchone()[0]

def get_user_config(user_id):
    cursor.execute("SELECT server_id, config_id, config_url FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def delete_user_config(user_id):
    server_info = get_user_config(user_id)
    if server_info:
        server_id = server_info[0]
        decrement_server_user_count(server_id)
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()

def get_all_users_with_config():
    cursor.execute("SELECT user_id, server_id, config_id FROM users")
    return cursor.fetchall()