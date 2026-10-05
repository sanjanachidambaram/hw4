"""Append-only audit trail of the chatbot's tool calls (output/audit_trail.json).

Each time the agent uses a tool, one short entry is recorded:
    {"time", "tool", "inputs", "result", "stop_reason"}

- Entries are collected during a chat turn and written together when the turn
  ends, because the stop reason ("answered", "usage_limit", "content_filter",
  "error") is only known then.
- The file is only ever appended to. It's never wiped or reset. Writes go to a
  temp file that is then swapped in, so a crash mid-write can't leave broken JSON.
- If the file is ever unreadable, it's moved aside (not deleted) and a new one
  is started.
- Nothing here can break a chat reply: every failure is caught and logged.
- No personal info is recorded: only tool names, short inputs, and short results.
"""

import functools
import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger("campus_customs.audit")

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"
MAX_TEXT = 80  # longest any single input or result summary can be

_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _short(text: str, limit: int = MAX_TEXT) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def summarize_inputs(kwargs: dict[str, Any]) -> str:
    """e.g. {'query': 'navy hoodie', 'limit': 6} -> 'query="navy hoodie", limit=6'."""
    parts = []
    for key, value in kwargs.items():
        if value is None:
            continue
        if isinstance(value, str):
            parts.append(f'{key}="{_short(value, 40)}"')
        elif isinstance(value, (list, tuple)):
            parts.append(f"{key}=[{', '.join(_short(v, 30) for v in value[:3])}{', …' if len(value) > 3 else ''}]")
        else:
            parts.append(f"{key}={value}")
    return _short(", ".join(parts)) or "(none)"


def summarize_result(tool: str, result: Any) -> str:
    """A few words about what a tool returned, instead of the whole thing."""
    try:
        if isinstance(result, dict) and "error" in result:
            return _short(f"error: {result['error']}")
        if getattr(result, "found", True) is False:  # ProductNotFound
            return _short(f"not found: {result.product_id}")
        if tool == "search_catalogue":
            if not result:
                return "no matches"
            return f"found {len(result)} product{'' if len(result) == 1 else 's'}"
        if tool == "get_product_details":
            in_stock = sum(1 for s in result.stock if s.quantity > 0)
            return _short(f"{result.name}, ${result.price:.2f}, {in_stock} of {len(result.stock)} sizes in stock")
        if tool == "check_size_stock":
            if result.status == "product_not_found":
                return _short(f"not found: {result.product_id}")
            qty = f" ({result.quantity})" if result.status == "in_stock" else ""
            return _short(f"{result.name} size {result.size}: {result.status}{qty}")
        if tool == "find_similar_products":
            return _short(f"{len(result.items)} similar items for {result.for_product_name}")
        if tool == "compare_products":
            text = f"compared {len(result.products)} products"
            if result.not_found:
                text += f"; {len(result.not_found)} not found"
            return _short(text)
    except Exception:  # an odd result shape should never break auditing
        pass
    return _short(type(result).__name__)


def audited(tool_fn: Callable) -> Callable:
    """Wrap a tool so each call is recorded in ctx.deps.audit_entries.

    If the tool itself fails, the agent gets a short error message instead of
    a crash, so it can honestly say the lookup didn't work.
    """

    @functools.wraps(tool_fn)
    def wrapper(ctx, *args, **kwargs):
        name = tool_fn.__name__
        try:
            result = tool_fn(ctx, *args, **kwargs)
        except Exception:
            logger.exception("Tool %s failed", name)
            result = {"error": "The lookup failed. Tell the customer you couldn't check right now."}
        try:
            ctx.deps.audit_entries.append(
                {
                    "time": _now(),
                    "tool": name,
                    "inputs": summarize_inputs(kwargs or dict(enumerate(args))),
                    "result": summarize_result(name, result),
                }
            )
        except Exception:
            logger.warning("Couldn't record audit entry for %s", name, exc_info=True)
        return result

    return wrapper


def _read_existing() -> list:
    """Load existing entries. If the contents are broken, move the file aside (never delete).

    If the file can't be opened at all (e.g. locked by another program), the
    OSError goes up to record(), which skips this write and leaves the file alone.
    """
    if not AUDIT_PATH.exists():
        return []
    text = AUDIT_PATH.read_text(encoding="utf-8")  # OSError -> skip this write
    try:
        data = json.loads(text or "[]")
        if isinstance(data, list):
            return data
        raise ValueError("audit trail is not a JSON list")
    except ValueError:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = AUDIT_PATH.with_name(f"audit_trail.unreadable-{stamp}.json")
        os.replace(AUDIT_PATH, backup)
        logger.warning("Audit trail was unreadable; kept it as %s and started a new one", backup.name)
        return []


def ensure_file() -> None:
    """Create an empty audit trail ([]) if none exists. Never touches an existing file."""
    try:
        with _lock:
            AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
            if not AUDIT_PATH.exists():
                AUDIT_PATH.write_text("[]\n", encoding="utf-8")
    except Exception:
        logger.warning("Couldn't create the audit trail file", exc_info=True)


def record(entries: list[dict], stop_reason: str) -> None:
    """Append this turn's tool entries with its stop reason. Never raises."""
    if not entries:
        return
    try:
        with _lock:
            AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
            data = _read_existing()
            data.extend({**e, "stop_reason": stop_reason} for e in entries)
            tmp = AUDIT_PATH.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(tmp, AUDIT_PATH)  # swap in the complete file in one step
    except Exception:
        logger.warning("Couldn't write the audit trail; the chat reply is unaffected", exc_info=True)
