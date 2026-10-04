"""Sets up the Campus Customs chatbot: instructions + model + tools.

The model is reached through Portkey, an AI gateway, using the
OpenAI-compatible connection described in the PydanticAI docs
(OpenAIProvider with a custom AsyncOpenAI client).

The PORTKEY_API_KEY is read from the course-folder .env (one level above
HW4), so the key is never copied into this project.
"""

import os
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values
from openai import AsyncOpenAI
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits

from models import AgentReply
from tools import ALL_TOOLS, ChatDeps

BACKEND_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BACKEND_DIR / "prompts" / "prompt.md"
COURSE_ENV_PATH = BACKEND_DIR.parent.parent / ".env"  # AI Foundations/.env

MODEL_NAME = "gpt-5.6-luna"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"

# Budget guards: every AI round-trip costs real money, so cap round-trips and
# tokens. Tool calls themselves are free local database reads, and the AI
# often makes several at once in one round-trip, so their cap is looser.
MODEL_SETTINGS = ModelSettings(max_tokens=600, timeout=30)
USAGE_LIMITS = UsageLimits(request_limit=5, tool_calls_limit=12, input_tokens_limit=40_000)

# How much earlier conversation the AI sees, counted in back-and-forth turns.
HISTORY_TURNS = 6
MAX_CONVERSATIONS = 500


class ChatUnavailable(RuntimeError):
    """The chatbot isn't configured (for example, the API key is missing)."""


def _load_portkey_key() -> str:
    key = os.getenv("PORTKEY_API_KEY") or dotenv_values(COURSE_ENV_PATH).get("PORTKEY_API_KEY")
    if not key:
        raise ChatUnavailable(f"PORTKEY_API_KEY not found in {COURSE_ENV_PATH}")
    return key


@lru_cache(maxsize=1)
def get_agent() -> Agent[ChatDeps, AgentReply]:
    """Build the agent once, the first time someone chats."""
    key = _load_portkey_key()
    client = AsyncOpenAI(
        api_key="portkey",  # placeholder; Portkey authenticates with the header below
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": key, "x-portkey-provider": "openai"},
    )
    model = OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))

    agent = Agent(
        model,
        deps_type=ChatDeps,
        output_type=AgentReply,  # reply text + product_ids to show as cards
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        tools=ALL_TOOLS,
        model_settings=MODEL_SETTINGS,
    )

    @agent.instructions
    def customer_name(ctx) -> str:
        if ctx.deps.first_name:
            return f"The customer is logged in. Their first name is {ctx.deps.first_name}."
        return "The customer is not logged in."

    return agent


# ---------- Conversation memory ----------
# Kept in server memory (resets when the server restarts), keyed by a random
# id stored in the visitor's signed session cookie. Each entry is a list of
# turns; each turn is the complete set of messages from one question+answer,
# so trimming never splits a tool call from its result.

_conversations: "OrderedDict[str, list[list[ModelMessage]]]" = OrderedDict()


def get_history(chat_id: str) -> list[ModelMessage]:
    turns = _conversations.get(chat_id, [])
    return [message for turn in turns for message in turn]


def save_turn(chat_id: str, new_messages: list[ModelMessage]) -> None:
    turns = _conversations.setdefault(chat_id, [])
    turns.append(new_messages)
    del turns[:-HISTORY_TURNS]
    _conversations.move_to_end(chat_id)
    while len(_conversations) > MAX_CONVERSATIONS:
        _conversations.popitem(last=False)


async def ask(message: str, chat_id: str, first_name: str | None) -> tuple[AgentReply, ChatDeps]:
    """Send one customer message to the agent and return its reply.

    Returns the AI's AgentReply (text + product_ids) and the deps, whose
    seen_ids lists every product a tool actually returned this turn.
    """
    deps = ChatDeps(first_name=first_name)
    result = await get_agent().run(
        message,
        deps=deps,
        message_history=get_history(chat_id),
        usage_limits=USAGE_LIMITS,
    )
    save_turn(chat_id, result.new_messages())
    return result.output, deps
