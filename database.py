import sqlite3

from werkzeug.security import generate_password_hash

DB_PATH = "users.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()

    # Tabela segura: guarda apenas o hash da senha
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )

    # Tabela do laboratório vulnerável: texto puro DE PROPÓSITO
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users_inseguro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    conn.execute(
        "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
        ("admin", generate_password_hash("admin123")),
    )
    conn.execute(
        "INSERT OR IGNORE INTO users_inseguro (username, password) VALUES (?, ?)",
        ("admin", "admin123"),
    )
    conn.commit()
    conn.close()