"""Campus Customs backend.

A small FastAPI app that reads the product catalogue and inventory from
data/campus_customs.db and serves them (plus product images) to the
React front end. It also handles creating accounts and logging in.

Safety notes:
- Product endpoints open the database READ-ONLY. Only account creation
  opens it for writing, and only to insert into the `users` table.
- Emails and password hashes are never sent to the browser. /api/auth/me
  returns only the logged-in user's first and last name. The chat agent
  gets first name, last name, and email, never the password hash.
- Saved chat history is always filtered by the user_id from the signed
  login cookie, so shoppers only ever see their own messages.
- Images are looked up by product_id through the database, never by a raw
  file path from the request, so a visitor can't ask for arbitrary files.
- See auth.py and output/harness.md for how passwords are protected.
"""

import json
import logging
import os
import secrets
import sqlite3
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from pydantic_ai.exceptions import ModelHTTPError, UsageLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

import agent
import auth
import history as chat_history
from models import (
    ChatHistoryMessage,
    ChatHistoryResponse,
    ChatProductCard,
    ChatRequest,
    ChatResponse,
    PageInfo,
)
from tools import ChatDeps, Customer, PageContext

logger = logging.getLogger("campus_customs")

BASE_DIR = Path(__file__).resolve().parent.parent  # the HW4 folder
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
IMAGES_DIR = (DATA_DIR / "products").resolve()

load_dotenv(Path(__file__).resolve().parent / ".env")
SESSION_SECRET = os.getenv("SESSION_SECRET", "")
if len(SESSION_SECRET) < 32 or SESSION_SECRET == "change-me":
    raise RuntimeError(
        "SESSION_SECRET is missing or too short. Copy backend/.env.example to "
        "backend/.env and set a long random value."
    )
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
SESSION_MAX_AGE = 7 * 24 * 60 * 60  # logged-in sessions expire after 7 days

# Show sizes in a sensible order instead of alphabetically.
SIZE_ORDER = {"XS": 0, "S": 1, "M": 2, "L": 3, "XL": 4, "XXL": 5}

# Only the React dev server is allowed to call this API from a browser.
FRONTEND_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

# Login limits: a burst of wrong guesses gets temporarily blocked.
login_limiter_ip = auth.RateLimiter(max_attempts=10, window_seconds=15 * 60)
login_limiter_email = auth.RateLimiter(max_attempts=5, window_seconds=15 * 60)
signup_limiter_ip = auth.RateLimiter(max_attempts=5, window_seconds=60 * 60)

# Hide the auto-generated API docs pages, which would map out every endpoint
# for an attacker.
app = FastAPI(title="Campus Customs API", docs_url=None, redoc_url=None, openapi_url=None)

# Make sure the chat history table exists (e.g. on a computer with a fresh
# database). Safe to run every time; it never changes existing data.
chat_history.ensure_chat_table()


@app.middleware("http")
async def security_checks(request: Request, call_next):
    # Block form posts coming from other websites (CSRF protection). Browsers
    # always send an Origin header on these, and it must be our front end.
    if request.method == "POST":
        origin = request.headers.get("origin")
        if origin is not None and origin not in FRONTEND_ORIGINS:
            return JSONResponse({"detail": "Forbidden"}, status_code=403)

    response = await call_next(request)

    # Standard protective headers.
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    if request.url.path.startswith("/api/auth"):
        response.headers["Cache-Control"] = "no-store"
    return response


# Logged-in state lives in a signed cookie. The signature uses SESSION_SECRET,
# so it can't be forged or edited. The cookie is HttpOnly, so page scripts
# can't read it, and SameSite=Lax, so other sites can't send it.
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="cc_session",
    max_age=SESSION_MAX_AGE,
    same_site="lax",
    https_only=COOKIE_SECURE,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,  # lets the browser send the login cookie
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def get_db() -> sqlite3.Connection:
    """Open a read-only connection to the database."""
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_writable_db() -> sqlite3.Connection:
    """Open a connection that can write. Only used to create accounts."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def product_from_row(row: sqlite3.Row) -> dict:
    """Turn a catalogue row into the JSON shape the front end expects."""
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "price": row["price"],
        "image_url": f"/api/images/{row['product_id']}",
    }


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/products")
def list_products() -> list[dict]:
    """Every product in the catalogue, with its total stock across sizes."""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM catalogue c
            LEFT JOIN inventory i ON i.product_id = c.product_id
            GROUP BY c.product_id
            ORDER BY c.name
            """
        ).fetchall()
    return [{**product_from_row(r), "total_stock": r["total_stock"]} for r in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    """One product's full details, including stock for each size."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        sizes = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?",
            (product_id,),
        ).fetchall()

    inventory = sorted(
        ({"size": s["size"], "quantity": s["quantity"]} for s in sizes),
        key=lambda s: SIZE_ORDER.get(s["size"], 99),
    )
    return {
        **product_from_row(row),
        "inventory": inventory,
        "total_stock": sum(s["quantity"] for s in inventory),
    }


@app.get("/api/images/{product_id}")
def get_image(product_id: str) -> FileResponse:
    """Serve a product's photo, looked up through the catalogue table."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT image_file_path FROM catalogue WHERE product_id = ?",
            (product_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")

    image_path = (DATA_DIR / row["image_file_path"]).resolve()
    # Extra guard: only ever serve files that live inside data/products/.
    if not image_path.is_relative_to(IMAGES_DIR) or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)


# ---------- Accounts ----------

class SignupRequest(BaseModel):
    first_name: str = Field(max_length=auth.MAX_NAME_LENGTH)
    last_name: str = Field(max_length=auth.MAX_NAME_LENGTH)
    email: str = Field(max_length=auth.MAX_EMAIL_LENGTH)
    password: str = Field(max_length=auth.MAX_PASSWORD_LENGTH)


class LoginRequest(BaseModel):
    email: str = Field(max_length=auth.MAX_EMAIL_LENGTH)
    password: str = Field(max_length=auth.MAX_PASSWORD_LENGTH)


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def public_user(row: sqlite3.Row) -> dict:
    """The only user details the browser ever receives."""
    return {"first_name": row["first_name"], "last_name": row["last_name"]}


def start_session(request: Request, user_id: int) -> None:
    request.session.clear()  # drop anything from before logging in
    request.session["user_id"] = user_id


@app.post("/api/auth/signup", status_code=201)
def signup(body: SignupRequest, request: Request) -> dict:
    ip = client_ip(request)
    if signup_limiter_ip.is_blocked(ip):
        raise HTTPException(429, "Too many sign-up attempts. Please try again later.")
    signup_limiter_ip.record(ip)

    first_name, last_name = body.first_name.strip(), body.last_name.strip()
    email = auth.normalize_email(body.email)
    error = auth.validate_signup(first_name, last_name, email, body.password)
    if error:
        raise HTTPException(400, error)

    password_hash = auth.hash_password(body.password)
    with closing(get_writable_db()) as conn:
        taken = conn.execute(
            "SELECT 1 FROM users WHERE lower(email) = ?", (email,)
        ).fetchone()
        if taken:
            raise HTTPException(409, "An account with that email already exists.")
        try:
            with conn:  # commits on success, rolls back on error
                cur = conn.execute(
                    """
                    INSERT INTO users (name, email, password_hash, first_name, last_name)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (f"{first_name} {last_name}", email, password_hash, first_name, last_name),
                )
        except sqlite3.IntegrityError:  # someone else took the email a moment ago
            raise HTTPException(409, "An account with that email already exists.")
        user_id = cur.lastrowid

    start_session(request, user_id)
    return {"first_name": first_name, "last_name": last_name}


@app.post("/api/auth/login")
def login(body: LoginRequest, request: Request) -> dict:
    ip = client_ip(request)
    email = auth.normalize_email(body.email)
    if login_limiter_ip.is_blocked(ip) or login_limiter_email.is_blocked(email):
        raise HTTPException(429, "Too many login attempts. Please wait 15 minutes and try again.")

    with closing(get_db()) as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE lower(email) = ?", (email,)
        ).fetchone()

    # Always run a hash check, even for unknown emails, so both cases take
    # the same time and give the same message.
    stored_hash = user["password_hash"] if user else auth.DUMMY_HASH
    password_ok = auth.verify_password(body.password, stored_hash)
    if not user or not password_ok:
        login_limiter_ip.record(ip)
        login_limiter_email.record(email)
        raise HTTPException(401, "Incorrect email or password.")

    login_limiter_email.reset(email)
    start_session(request, user["id"])
    return public_user(user)


@app.post("/api/auth/logout")
def logout(request: Request) -> dict:
    request.session.clear()
    return {"ok": True}


@app.get("/api/auth/me")
def me(request: Request) -> dict:
    """Who is logged in right now (or null if nobody)."""
    user_id = request.session.get("user_id")
    if user_id is None:
        return {"user": None}
    with closing(get_db()) as conn:
        user = conn.execute(
            "SELECT first_name, last_name FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    if user is None:  # account no longer exists
        request.session.clear()
        return {"user": None}
    return {"user": public_user(user)}


# ---------- Chat ----------

# Every AI message costs money, so cap how fast one visitor can send them.
chat_limiter_ip = auth.RateLimiter(max_attempts=20, window_seconds=10 * 60)

# Map site paths to simple page names. Only these names reach the AI, never
# the raw path the browser sent.
PAGE_NAMES = {"/": "home", "/products": "products", "/about": "about",
              "/login": "login", "/signup": "signup"}

FILTERED_REPLY = "Sorry, I can't help with that. I'm here to help with Campus Customs products, prices, and sizes!"


def current_customer(request: Request) -> tuple[int | None, Customer | None]:
    """The logged-in user's id and name/email from the signed cookie, or (None, None) for a guest.

    Only first name, last name, and email are read. The password hash is never selected.
    """
    user_id = request.session.get("user_id")
    if user_id is None:
        return None, None
    with closing(get_db()) as conn:
        row = conn.execute(
            "SELECT first_name, last_name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    if row is None:
        return None, None
    return user_id, Customer(
        first_name=row["first_name"] or "", last_name=row["last_name"] or "", email=row["email"]
    )


def page_context(page: PageInfo | None) -> PageContext | None:
    """Turn the browser's page info into trusted context for the agent.

    The product id is checked against the catalogue, and the product name is
    read from the database, so nothing the browser sends is passed through as-is.
    """
    if page is None:
        return None
    if page.product_id:
        with closing(get_db()) as conn:
            row = conn.execute(
                "SELECT product_id, name FROM catalogue WHERE product_id = ?", (page.product_id,)
            ).fetchone()
        if row:
            return PageContext(page="product", product_id=row["product_id"], product_name=row["name"])
    return PageContext(page=PAGE_NAMES.get(page.path, "other"))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    """Send the customer's message to the AI agent and return its reply."""
    ip = client_ip(request)
    if chat_limiter_ip.is_blocked(ip):
        raise HTTPException(429, "You're sending messages quickly. Please wait a few minutes.")
    chat_limiter_ip.record(ip)

    user_id, customer = current_customer(request)
    deps = ChatDeps(customer=customer, page=page_context(body.page))

    # Logged in: earlier conversation comes from the database (survives
    # restarts and logouts). Guest: from server memory only, never saved.
    chat_id = None
    if user_id is not None:
        history = chat_history.as_agent_history(user_id)
    else:
        chat_id = request.session.get("chat_id")
        if not chat_id:
            chat_id = secrets.token_urlsafe(16)
            request.session["chat_id"] = chat_id
        history = agent.get_history(chat_id)

    try:
        reply, new_messages = await agent.ask(body.message, deps, history)
    except agent.ChatUnavailable:
        logger.error("Chat is not configured: PORTKEY_API_KEY is missing.")
        raise HTTPException(503, "The shop assistant isn't available right now.")
    except UsageLimitExceeded:
        return ChatResponse(reply="Sorry, that one took me too long to look up. Could you ask it a simpler way?")
    except ModelHTTPError as exc:
        # The AI provider's safety filter blocks messages that look like attempts
        # to break the assistant's rules. Treat that as a polite refusal, and
        # don't save it (it could trip the filter again on later messages).
        if "content_filter" in str(exc.body):
            logger.warning("Chat message blocked by the provider's content filter.")
            return ChatResponse(reply=FILTERED_REPLY)
        logger.exception("Chat request failed")
        raise HTTPException(502, "The shop assistant ran into a problem. Please try again.")
    except Exception:
        # Log the details for us, but don't show internals to the visitor.
        logger.exception("Chat request failed")
        raise HTTPException(502, "The shop assistant ran into a problem. Please try again.")

    cards = build_product_cards(reply.product_ids, allowed_ids=deps.seen_ids)
    if user_id is not None:
        chat_history.save_exchange(user_id, body.message, reply.reply, [c.product_id for c in cards])
    else:
        agent.save_turn(chat_id, new_messages)
    return ChatResponse(reply=reply.reply, products=cards)


@app.get("/api/chat/history", response_model=ChatHistoryResponse)
def get_chat_history(request: Request) -> ChatHistoryResponse:
    """The logged-in shopper's own saved messages. Guests always get an empty list."""
    user_id, _ = current_customer(request)
    if user_id is None:
        return ChatHistoryResponse(messages=[])
    messages = []
    for row in chat_history.load_recent(user_id, chat_history.DISPLAY_MESSAGES):
        ids = chat_history.product_ids_from_json(row["products_json"])
        messages.append(
            ChatHistoryMessage(
                role=row["role"],
                content=row["content"],
                products=load_product_cards(ids) if row["role"] == "assistant" else [],
            )
        )
    return ChatHistoryResponse(messages=messages)


MAX_CHAT_CARDS = 8


def build_product_cards(product_ids: list[str], allowed_ids: set[str]) -> list[ChatProductCard]:
    """Turn the AI's chosen product ids into real cards from the database.

    Only ids that a tool actually returned this turn are kept, so the AI
    can't invent a product.
    """
    return load_product_cards([pid for pid in product_ids if pid in allowed_ids])


def load_product_cards(product_ids: list[str]) -> list[ChatProductCard]:
    """Fresh card details (name, price, image, stock) straight from the database.

    Duplicates are dropped, unknown ids are skipped, and at most 8 are returned.
    """
    wanted = list(dict.fromkeys(product_ids))[:MAX_CHAT_CARDS]
    if not wanted:
        return []
    placeholders = ",".join("?" * len(wanted))
    with closing(get_db()) as conn:
        rows = conn.execute(
            f"""
            SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM catalogue c
            LEFT JOIN inventory i ON i.product_id = c.product_id
            WHERE c.product_id IN ({placeholders})
            GROUP BY c.product_id
            """,
            wanted,
        ).fetchall()
    by_id = {r["product_id"]: r for r in rows}
    return [
        ChatProductCard(
            product_id=r["product_id"],
            name=r["name"],
            price=r["price"],
            description=r["description"],
            image_url=f"/api/images/{r['product_id']}",
            total_stock=r["total_stock"],
        )
        for pid in wanted
        if (r := by_id.get(pid)) is not None
    ]
