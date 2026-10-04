"""Pydantic types for what the chat box sends and what it gets back."""

from pydantic import BaseModel, Field

MAX_MESSAGE_LENGTH = 1000


class ChatRequest(BaseModel):
    """What the chat box sends to POST /api/chat."""

    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)


class ProductLink(BaseModel):
    """A product the assistant looked up, so the chat box can link to it."""

    product_id: str
    name: str
    price: float


class ChatResponse(BaseModel):
    """What POST /api/chat sends back to the chat box."""

    reply: str
    products: list[ProductLink] = Field(
        default_factory=list,
        description="Products the assistant looked up while answering.",
    )
