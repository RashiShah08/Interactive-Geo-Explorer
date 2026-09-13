import sqlite3

import bcrypt

from src.auth.db import get_connection


def signup(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not username or not password:
        return False, "All fields are required."

    conn = get_connection()
    try:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
        return True, "Sign up successful! Please log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


def login(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not username or not password:
        return False, "All fields are required."

    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return False, "Invalid username or password."

    password_hash = row[0]
    if bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
        return True, f"Welcome, {username}!"
    return False, "Invalid username or password."
