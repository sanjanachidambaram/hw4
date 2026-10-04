"""Password hashing, input checks, and login rate limiting for Campus Customs.

Password storage format (in users.password_hash):
- Existing accounts:  pbkdf2_sha256$<salt>$<hash>               (120,000 rounds)
- New accounts:       pbkdf2_sha256$<rounds>$<salt>$<hash>      (600,000 rounds)

The new format records the round count, so it can be raised later without
breaking older accounts.
"""

import hashlib
import hmac
import re
import secrets
import threading
import time
from collections import defaultdict, deque

ALGORITHM = "pbkdf2_sha256"
LEGACY_ITERATIONS = 120_000  # what the provided database's accounts use
ITERATIONS = 600_000  # OWASP's recommended minimum for PBKDF2-SHA256

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128  # stops someone sending a huge password to slow the server
MAX_NAME_LENGTH = 50
MAX_EMAIL_LENGTH = 254

# A few passwords so common that attackers always try them first.
COMMON_PASSWORDS = {
    "password", "password1", "password123", "12345678", "123456789",
    "1234567890", "qwerty123", "qwertyuiop", "iloveyou", "letmein1",
    "11111111", "00000000", "abc12345", "yaleyale", "bulldogs",
}

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _pbkdf2(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    ).hex()


def hash_password(password: str) -> str:
    """Return a salted, slow hash of the password. The password itself is never stored."""
    salt = secrets.token_hex(16)
    return f"{ALGORITHM}${ITERATIONS}${salt}${_pbkdf2(password, salt, ITERATIONS)}"


def verify_password(password: str, stored: str) -> bool:
    """Check a password against a stored hash (supports both formats)."""
    parts = stored.split("$")
    if len(parts) == 3:
        algorithm, salt, expected = parts
        iterations = LEGACY_ITERATIONS
    elif len(parts) == 4:
        algorithm, rounds, salt, expected = parts
        if not rounds.isdigit():
            return False
        iterations = int(rounds)
    else:
        return False
    if algorithm != ALGORITHM:
        return False
    # compare_digest takes the same time whether the first or last character
    # differs, so attackers can't guess the hash by timing responses.
    return hmac.compare_digest(_pbkdf2(password, salt, iterations), expected)


# Used when the email doesn't exist, so a failed login takes the same time
# either way and doesn't reveal which emails have accounts.
DUMMY_HASH = hash_password(secrets.token_hex(16))


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_signup(first_name: str, last_name: str, email: str, password: str) -> str | None:
    """Return an error message for bad signup input, or None if it's fine."""
    if not first_name.strip() or not last_name.strip():
        return "Please enter your first and last name."
    if len(first_name.strip()) > MAX_NAME_LENGTH or len(last_name.strip()) > MAX_NAME_LENGTH:
        return f"Names must be {MAX_NAME_LENGTH} characters or fewer."
    if len(email) > MAX_EMAIL_LENGTH or not EMAIL_PATTERN.match(email):
        return "Please enter a valid email address."
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if len(password) > MAX_PASSWORD_LENGTH:
        return f"Password must be {MAX_PASSWORD_LENGTH} characters or fewer."
    if password.lower() in COMMON_PASSWORDS:
        return "That password is too common. Please choose a different one."
    if password.lower() == email.lower() or password.lower() == email.split("@")[0].lower():
        return "Password can't be the same as your email."
    return None


class RateLimiter:
    """Blocks a key (e.g. an IP address) after too many attempts in a time window.

    Kept in memory, so it resets when the server restarts. That's fine for a
    class project; a real site would store this in something like Redis.
    """

    def __init__(self, max_attempts: int, window_seconds: int):
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, key: str, now: float) -> deque[float]:
        attempts = self._attempts[key]
        while attempts and now - attempts[0] > self.window:
            attempts.popleft()
        return attempts

    def is_blocked(self, key: str) -> bool:
        with self._lock:
            return len(self._prune(key, time.monotonic())) >= self.max_attempts

    def record(self, key: str) -> None:
        with self._lock:
            now = time.monotonic()
            self._prune(key, now).append(now)

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)
