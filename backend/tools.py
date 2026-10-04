"""Read-only database lookups the chatbot can use.

Every function here opens the database in READ-ONLY mode, so the AI can't
change anything even if it tried. None of them touch the `users` table.
"""

import json
import re
import sqlite3
from contextlib import closing
from typing import Literal
from dataclasses import dataclass, field
from pathlib import Path

from pydantic_ai import RunContext

from models import (
    CatalogueMatch,
    ProductDetails,
    ProductNotFound,
    SizeStock,
    SizeStockResult,
)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "campus_customs.db"
SIZE_ORDER = {"XS": 0, "S": 1, "M": 2, "L": 3, "XL": 4, "XXL": 5}
# Different words customers use for the same thing, mapped to the word the
# catalogue uses ("grey" -> "gray", "tee" -> "shirt").
QUERY_SYNONYMS = {
    "grey": "gray", "tee": "shirt", "tees": "shirt", "tshirt": "shirt", "tshirts": "shirt",
    "hoody": "hoodie", "hoodys": "hoodie", "jumper": "sweater",
    "sweatshirts": "sweatshirt", "quarterzip": "zip", "fleeces": "fleece",
}

DEFAULT_LIMIT = 6
MAX_LIMIT = 12

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
    "a", "an", "and", "any", "anything", "do", "does", "for", "got", "have", "i",
    "in", "is", "it", "items", "like", "looking", "me", "of", "on", "or", "please",
    "sell", "show", "some", "something", "stuff", "that", "the", "what", "with",
    "you", "your", "yale",
}


@dataclass
class Customer:
    """Who is chatting. Only these three fields; never a password or hash."""

    first_name: str
    last_name: str
    email: str


@dataclass
class PageContext:
    """Where the shopper is on the site when they send the message."""

    page: str  # "home", "products", "product", "about", "login", "signup", or "other"
    product_id: str | None = None  # set only on a product page, and only if it exists
    product_name: str | None = None  # read from the database, not from the browser


@dataclass
class ChatDeps:
    """The agent's "backpack": per-message info its tools and instructions can see.

    Passed to agent.run(deps=...) and read as ctx.deps (PydanticAI's
    dependency pattern).
    """

    customer: Customer | None = None  # None means a guest
    page: PageContext | None = None
    # Every product id a tool returned during this turn. The AI may only show
    # cards for these, so it can't invent a product.
    seen_ids: set[str] = field(default_factory=set)


def _read_only_db() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _remember(ctx: RunContext[ChatDeps], row: sqlite3.Row) -> None:
    ctx.deps.seen_ids.add(row["product_id"])


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _word_matches(word: str, words: set[str]) -> bool:
    """True if the whole word, or its singular ("hoodies" -> "hoodie"), appears.

    Whole words only, so "shirt" doesn't match inside "sweatshirt".
    """
    if word in words:
        return True
    if len(word) > 3 and word.endswith("es") and word[:-2] in words:
        return True
    return len(word) > 3 and word.endswith("s") and word[:-1] in words


def search_catalogue(
    ctx: RunContext[ChatDeps],
    query: str,
    limit: int = DEFAULT_LIMIT,
    sort: Literal["relevance", "price_low", "price_high"] = "relevance",
) -> list[CatalogueMatch]:
    """Search the catalogue by product name, category, description, and colors (capital letters don't matter).

    Every meaningful word in the query must match, so "navy hoodie" finds
    navy hoodies, not every navy item. Plurals are fine ("hoodies").

    Args:
        query: What the customer wants, e.g. "hoodies", "navy crewneck", "Saybrook".
        limit: Most results to return (1-12, default 6).
        sort: "relevance" (default), "price_low" (cheapest first), or
            "price_high" (most expensive first). Use a price sort for
            "cheapest" / "most expensive" questions, since a search can match
            more products than the limit returns.

    Returns:
        Matching products (id, name, category, colors, price, in_stock), best
        matches first. This is enough to answer "do you have a gray shirt?"
        without looking up each product. An empty list means nothing in the
        catalogue matches. This is not an error.
    """
    words = [
        QUERY_SYNONYMS.get(w, w) for w in re.findall(r"[a-z0-9]+", query.lower())
        if w not in STOPWORDS and len(w) > 1
    ]
    if not words:
        return []
    limit = max(1, min(limit, MAX_LIMIT))

    with closing(_read_only_db()) as conn:
        rows = conn.execute(
            """
            SELECT c.product_id, c.name, c.garment_type, c.description, c.colors, c.price,
                   COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM catalogue c
            LEFT JOIN inventory i ON i.product_id = c.product_id
            GROUP BY c.product_id
            """
        ).fetchall()

    scored = []
    for row in rows:
        title_words = _words(f"{row['name']} {row['garment_type']}")
        color_words = _words(" ".join(json.loads(row["colors"])))
        all_words = title_words | color_words | _words(row["description"])
        if not all(_word_matches(w, all_words) for w in words):
            continue
        # Rank name/category matches highest, then listed colors, then
        # words that only appear somewhere in the description.
        score = sum(
            2 if _word_matches(w, title_words) else 1 if _word_matches(w, color_words) else 0
            for w in words
        )
        scored.append((score, row))

    if sort == "price_low":
        scored.sort(key=lambda pair: (pair[1]["price"], pair[1]["name"]))
    elif sort == "price_high":
        scored.sort(key=lambda pair: (-pair[1]["price"], pair[1]["name"]))
    else:
        scored.sort(key=lambda pair: (-pair[0], pair[1]["name"]))
    results = []
    for _, row in scored[:limit]:
        _remember(ctx, row)
        results.append(
            CatalogueMatch(
                product_id=row["product_id"],
                name=row["name"],
                category=row["garment_type"],
                colors=json.loads(row["colors"]),
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
        product_id: The product_id from search_catalogue, e.g. "basic-hoodie-big-yale".

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
        product_id: The product_id from search_catalogue.
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


ALL_TOOLS = [search_catalogue, get_product_details, check_size_stock]
