import os
import sqlite3
import threading
import time

from config import DB_PATH

_lock = threading.Lock()
_conn = None


def init():
    global _conn
    directory = os.path.dirname(os.path.abspath(DB_PATH))
    if directory:
        os.makedirs(directory, exist_ok=True)
    _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    _conn.row_factory = sqlite3.Row
    with _lock:
        _conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                banned      INTEGER NOT NULL DEFAULT 0,
                searches    INTEGER NOT NULL DEFAULT 0,
                found       INTEGER NOT NULL DEFAULT 0,
                joined_at   INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS matches (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                title       TEXT,
                artist      TEXT,
                created_at  INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_matches_user ON matches (user_id);
            """
        )
        _conn.commit()


def _exec(query, params=(), fetch=None):
    with _lock:
        cur = _conn.execute(query, params)
        if fetch == 'one':
            row = cur.fetchone()
        elif fetch == 'all':
            row = cur.fetchall()
        else:
            row = cur.lastrowid
        _conn.commit()
        return row


# ---------- users ----------

def save_user(user):
    _exec(
        'INSERT INTO users (user_id, username, first_name, joined_at) VALUES (?, ?, ?, ?) '
        'ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, first_name=excluded.first_name',
        (user.id, user.username, user.first_name, int(time.time())),
    )


def get_user(user_id: int):
    return _exec('SELECT * FROM users WHERE user_id = ?', (user_id,), 'one')


def is_banned(user_id: int) -> bool:
    row = _exec('SELECT banned FROM users WHERE user_id = ?', (user_id,), 'one')
    return bool(row and row['banned'])


def set_banned(user_id: int, banned: bool):
    _exec('INSERT OR IGNORE INTO users (user_id, joined_at) VALUES (?, ?)', (user_id, int(time.time())))
    _exec('UPDATE users SET banned = ? WHERE user_id = ?', (1 if banned else 0, user_id))


def all_user_ids():
    rows = _exec('SELECT user_id FROM users WHERE banned = 0', (), 'all') or []
    return [r['user_id'] for r in rows]


# ---------- statistiques ----------

def add_search(user_id: int):
    _exec('UPDATE users SET searches = searches + 1 WHERE user_id = ?', (user_id,))


def add_match(user_id: int, title: str, artist: str):
    _exec('UPDATE users SET found = found + 1 WHERE user_id = ?', (user_id,))
    _exec(
        'INSERT INTO matches (user_id, title, artist, created_at) VALUES (?, ?, ?, ?)',
        (user_id, title, artist, int(time.time())),
    )


def global_stats():
    row = _exec(
        'SELECT COUNT(*) AS users, COALESCE(SUM(searches), 0) AS searches, '
        'COALESCE(SUM(found), 0) AS found FROM users',
        (),
        'one',
    )
    return dict(row) if row else {'users': 0, 'searches': 0, 'found': 0}
