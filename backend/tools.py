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

from models import (
    ProductDetails,
    ProductLink,
    ProductNotFound,
    ProductSearchResult,
    SizeStock,
    SizeStockResult,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"
SIZE_ORDER = {"XS": 0, "S": 1, "M": 2, "L": 3, "XL": 4, "XXL": 5}
MAX_RESULTS = 10

# Ways customers say sizes, mapped to how the database stores them.
SIZE_ALIASES = {
    "xs": "XS", "extra small": "XS", "x-small": "XS", "xsmall": "XS",
    "s": "S", "small": "S", "sm": "S",
    "m": "M", "medium": "M", "med": "M",
    "l": "L", "large": "L", "lg": "L",
    "xl": "XL", "extra large": "XL", "x-large": "XL", "xlarge": "XL",
    "xxl": "XXL", "2xl": "XXL", "xx-large": "XXL", "xxlarge": "XXL", "double xl": "XXL",
}

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
) -> list[ProductSearchResult]:
    """Search the shop's catalogue by keywords such as product type, color, college, sport, or name.

    Args:
        query: Keywords to search for, e.g. "navy hoodie", "Saybrook", "fleece".
        max_price: Optional highest price in US dollars.

    Returns:
        Up to 10 matching products (id, name, price, whether any size is in
        stock). An empty list means the shop doesn't carry anything matching.
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
            ProductSearchResult(
                product_id=row["product_id"],
                name=row["name"],
                price=row["price"],
                in_stock=row["total_stock"] > 0,
            )
        )
    return results


def _load_product(conn: sqlite3.Connection, product_id: str):
    """Fetch a product row and its sizes (in XS-XXL order), or (None, [])."""
    row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
    if row is None:
        return None, []
    sizes = conn.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    stock = sorted(
        (SizeStock(size=s["size"], quantity=s["quantity"]) for s in sizes),
        key=lambda s: SIZE_ORDER.get(s.size, 99),
    )
    return row, stock


def get_product_details(
    ctx: RunContext[ChatDeps], product_id: str
) -> ProductDetails | ProductNotFound:
    """Get one product's description, price, colors, and stock for every size.

    Args:
        product_id: The product_id from search_products, e.g. "basic-hoodie-big-yale".

    Returns:
        The product's details, with stock as a list of sizes and quantities
        (0 means sold out). If no product has that id, returns ProductNotFound.
    """
    with closing(_read_only_db()) as conn:
        row, stock = _load_product(conn, product_id)
    if row is None:
        return ProductNotFound(product_id=product_id, message=f"No product with id '{product_id}'.")

    _remember(ctx, row)
    return ProductDetails(
        product_id=row["product_id"],
        name=row["name"],
        price=row["price"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        stock=stock,
    )


def normalize_size(size: str) -> str:
    """Turn 'medium', 'm', or '2XL' into the database's form ('M', 'XXL')."""
    cleaned = " ".join(size.strip().lower().replace("size", "").split())
    return SIZE_ALIASES.get(cleaned, cleaned.upper())


def check_size_stock(ctx: RunContext[ChatDeps], product_id: str, size: str) -> SizeStockResult:
    """Check whether one specific size of a product is in stock.

    Args:
        product_id: The product_id from search_products.
        size: The size the customer asked about, e.g. "M", "medium", "XL", "2XL".

    Returns:
        status is one of: "in_stock" (with quantity), "sold_out",
        "size_not_offered" (this product doesn't come in that size), or
        "product_not_found". sizes_offered lists every size the product comes
        in; sizes_in_stock lists only the ones available now.
    """
    wanted = normalize_size(size)
    with closing(_read_only_db()) as conn:
        row, stock = _load_product(conn, product_id)

    if row is None:
        return SizeStockResult(
            product_id=product_id, name=None, size=wanted,
            status="product_not_found", quantity=0, sizes_offered=[], sizes_in_stock=[],
        )

    _remember(ctx, row)
    by_size = {s.size: s.quantity for s in stock}
    if wanted not in by_size:
        status, quantity = "size_not_offered", 0
    elif by_size[wanted] == 0:
        status, quantity = "sold_out", 0
    else:
        status, quantity = "in_stock", by_size[wanted]
    return SizeStockResult(
        product_id=row["product_id"], name=row["name"], size=wanted,
        status=status, quantity=quantity, sizes_offered=list(by_size),
        sizes_in_stock=[size for size, qty in by_size.items() if qty > 0],
    )


ALL_TOOLS = [search_products, get_product_details, check_size_stock]
