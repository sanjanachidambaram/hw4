"""Read-only database lookups the chatbot can use.

Every function here opens the database in READ-ONLY mode, so the AI can't
change anything even if it tried. None of them touch the `users` table.
"""

import json
import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path

from pydantic_ai import RunContext

from models import ProductLink

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"
SIZE_ORDER = {"XS": 0, "S": 1, "M": 2, "L": 3, "XL": 4, "XXL": 5}
MAX_RESULTS = 10

# Words that don't help find a product.
STOPWORDS = {
    "a", "an", "and", "any", "do", "for", "have", "i", "in", "is", "it", "me",
    "of", "on", "or", "show", "some", "the", "with", "you", "your", "yale",
}


@dataclass
class ChatDeps:
    """Per-message info the tools can see."""

    first_name: str | None = None  # only the first name, never email or password
    looked_up: dict[str, ProductLink] = field(default_factory=dict)


def _read_only_db() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _remember(ctx: RunContext[ChatDeps], row: sqlite3.Row) -> None:
    ctx.deps.looked_up[row["product_id"]] = ProductLink(
        product_id=row["product_id"], name=row["name"], price=row["price"]
    )


def search_products(
    ctx: RunContext[ChatDeps], query: str, max_price: float | None = None
) -> list[dict]:
    """Search the shop's catalogue by keywords such as product type, color, college, sport, or name.

    Args:
        query: Keywords to search for, e.g. "navy hoodie", "Saybrook", "fleece".
        max_price: Optional highest price in US dollars.

    Returns:
        Up to 10 matching products with product_id, name, garment type, price,
        colors, and total units in stock across all sizes. An empty list means
        the shop doesn't carry anything matching.
    """
    words = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if w not in STOPWORDS]
    if not words:
        return []

    with closing(_read_only_db()) as conn:
        rows = conn.execute(
            """
            SELECT c.product_id, c.name, c.garment_type, c.description, c.colors,
                   c.search_tags, c.price, COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM catalogue c
            LEFT JOIN inventory i ON i.product_id = c.product_id
            GROUP BY c.product_id
            """
        ).fetchall()

    scored = []
    for row in rows:
        if max_price is not None and row["price"] > max_price:
            continue
        haystack = " ".join(
            [row["name"], row["garment_type"], row["description"], row["colors"], row["search_tags"]]
        ).lower()
        score = sum(1 for w in words if w in haystack)
        if score:
            scored.append((score, row))

    scored.sort(key=lambda pair: (-pair[0], pair[1]["price"]))
    results = []
    for _, row in scored[:MAX_RESULTS]:
        _remember(ctx, row)
        results.append(
            {
                "product_id": row["product_id"],
                "name": row["name"],
                "garment_type": row["garment_type"],
                "price": row["price"],
                "colors": json.loads(row["colors"]),
                "total_stock": row["total_stock"],
            }
        )
    return results


def get_product_details(ctx: RunContext[ChatDeps], product_id: str) -> dict:
    """Get one product's full details, including price and units in stock for each size.

    Args:
        product_id: The product_id from search_products, e.g. "basic-hoodie-big-yale".

    Returns:
        The product's name, description, price, colors, and a list of sizes
        with quantity in stock (0 means sold out in that size). Returns an
        "error" key if no product has that id.
    """
    with closing(_read_only_db()) as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return {"error": f"No product with id '{product_id}'."}
        sizes = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()

    _remember(ctx, row)
    stock = sorted(
        ({"size": s["size"], "quantity": s["quantity"]} for s in sizes),
        key=lambda s: SIZE_ORDER.get(s["size"], 99),
    )
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "price": row["price"],
        "colors": json.loads(row["colors"]),
        "stock_by_size": stock,
        "total_stock": sum(s["quantity"] for s in stock),
    }


ALL_TOOLS = [search_products, get_product_details]
