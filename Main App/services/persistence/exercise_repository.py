import sqlite3
import streamlit as st
from pathlib import Path


# =========================================================
# DATABASE PATH
# =========================================================

_DB_PATH = str(
    Path(__file__).parent.parent.parent / "data.db"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

@st.cache_resource
def _get_connection() -> sqlite3.Connection:

    conn = sqlite3.connect(
        _DB_PATH,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db() -> None:

    conn = _get_connection()

    with conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL
                    REFERENCES users(id),
                exercise_name TEXT NOT NULL,
                reps INTEGER NOT NULL DEFAULT 0,
                sets INTEGER NOT NULL DEFAULT 0,
                time INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


# =========================================================
# GET USER
# =========================================================

def get_user(username: str) -> sqlite3.Row:

    conn = _get_connection()

    return conn.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()


# =========================================================
# CREATE USER
# =========================================================

def create_user(username: str) -> sqlite3.Row:

    conn = _get_connection()

    with conn:

        conn.execute(
            """
            INSERT INTO users (username)
            VALUES (?)
            """,
            (username,)
        )

    return get_user(username)


# =========================================================
# GET OR CREATE USER
# =========================================================

def get_or_create_user(username: str) -> sqlite3.Row:

    user = get_user(username)

    if user is None:

        user = create_user(username)

    return user


# =========================================================
# ADD WORKOUT
# =========================================================
# Every completed workout gets a NEW row.
# Same exercise + same date will NOT be merged.
# =========================================================

def add_exercise(
    user_id,
    exercise_name,
    reps,
    sets,
    time
):

    conn = _get_connection()

    with conn:

        conn.execute(
            """
            INSERT INTO exercises (
                user_id,
                exercise_name,
                reps,
                sets,
                time
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                int(user_id),
                str(exercise_name),
                int(reps),
                int(sets),
                int(time)
            )
        )


# =========================================================
# GET USER WORKOUT HISTORY
# =========================================================
# IMPORTANT:
# Only workouts from 9 September 2026 onward are shown.
# Older records remain safely stored in database.
# =========================================================

def get_users_exercises(user_id):

    conn = _get_connection()

    return conn.execute(
        """
        SELECT *
        FROM exercises
        WHERE user_id = ?
          AND date(created_at) >= '2026-09-09'
        ORDER BY datetime(created_at) DESC, id DESC
        """,
        (int(user_id),)
    ).fetchall()

