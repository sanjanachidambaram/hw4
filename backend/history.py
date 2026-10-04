"""Saved chat history for logged-in shoppers, stored in the chat_messages table.

Every query here filters by user_id, and user_id always comes from the
signed login cookie (never from the browser's request body), so one person
can never read or write another person's history.

Guests' chats are NOT saved here; agent.py keeps them in memory only.
"""

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"

# How many saved messages the AI sees as context (6 back-and-forths).
AGENT_CONTEXT_MESSAGES = 12
# How many saved messages the chat box shows when someone returns.
DISPLAY_MESSAGES = 50

# Same structure as the table in the provided database, so a fresh database
# on another computer ends up identical.
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    products_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
"""
CREATE_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_chat_messages_user ON chat_messages (user_id, id)"
)


def _connect(read_only: bool = False) -> sqlite3.Connection:
    if read_only:
        conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_chat_table() -> None:
    """Create chat_messages (and its index) if missing. Safe to run every startup."""
    with closing(_connect()) as conn, conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.execute(CREATE_INDEX_SQL)


def save_exchange(user_id: int, question: str, reply: str, product_ids: list[str]) -> None:
    """Save one question and its answer together, so we never store half a turn."""
    products_json = json.dumps([{"product_id": pid} for pid in product_ids]) if product_ids else None
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)",
            (user_id, question),
        )
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            (user_id, reply, products_json),
        )


def load_recent(user_id: int, limit: int) -> list[sqlite3.Row]:
    """This user's most recent messages, oldest first."""
    with closing(_connect(read_only=True)) as conn:
        rows = conn.execute(
            """
            SELECT role, content, products_json, created_at FROM chat_messages
            WHERE user_id = ? AND role IN ('user', 'assistant')
            ORDER BY id DESC LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return list(reversed(rows))


def product_ids_from_json(products_json: str | None) -> list[str]:
    """Read product ids from products_json, tolerating older or malformed data."""
    if not products_json:
        return []
    try:
        items = json.loads(products_json)
    except ValueError:
        return []
    if not isinstance(items, list):
        return []
    return [
        item["product_id"]
        for item in items
        if isinstance(item, dict) and isinstance(item.get("product_id"), str)
    ]


def as_agent_history(user_id: int) -> list[ModelMessage]:
    """Turn this user's saved messages into the format PydanticAI expects."""
    messages: list[ModelMessage] = []
    for row in load_recent(user_id, AGENT_CONTEXT_MESSAGES):
        if row["role"] == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=row["content"])]))
        else:
            messages.append(ModelResponse(parts=[TextPart(content=row["content"])]))
    # The history must start with a customer message, not a reply.
    while messages and isinstance(messages[0], ModelResponse):
        messages.pop(0)
    return messages
