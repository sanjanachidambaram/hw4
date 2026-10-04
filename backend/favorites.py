"""Saved favorites for logged-in shoppers, stored in a new `favorites` table.

Every query filters by user_id, and user_id always comes from the signed
login cookie (never from the browser's request), so a shopper only ever
sees or changes their own favorites.
"""

import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"

# A new table; existing tables are not touched. UNIQUE stops the same item
# being saved twice by the same person.
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (user_id, product_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES catalogue(product_id)
)
"""


def _connect(read_only: bool = False) -> sqlite3.Connection:
    if read_only:
        conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_favorites_table() -> None:
    """Create the favorites table if it's missing. Safe to run every startup."""
    with closing(_connect()) as conn, conn:
        conn.execute(CREATE_TABLE_SQL)


def list_ids(user_id: int) -> list[str]:
    """This user's saved product ids, newest first."""
    with closing(_connect(read_only=True)) as conn:
        rows = conn.execute(
            "SELECT product_id FROM favorites WHERE user_id = ? ORDER BY id DESC", (user_id,)
        ).fetchall()
    return [r["product_id"] for r in rows]


def add(user_id: int, product_id: str) -> None:
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT OR IGNORE INTO favorites (user_id, product_id) VALUES (?, ?)",
            (user_id, product_id),
        )


def remove(user_id: int, product_id: str) -> None:
    with closing(_connect()) as conn, conn:
        conn.execute(
            "DELETE FROM favorites WHERE user_id = ? AND product_id = ?", (user_id, product_id)
        )
