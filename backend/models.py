"""Pydantic types for the chat (what it sends and gets back) and for what
the chatbot's tools return."""

from typing import Literal

from pydantic import BaseModel, Field

MAX_MESSAGE_LENGTH = 1000


# ---------- Chat request / response ----------

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


# ---------- Tool results ----------

class SizeStock(BaseModel):
    """How many of one size are in stock."""

    size: str = Field(description="Size label, e.g. 'M' or 'XXL'.")
    quantity: int = Field(description="Units in stock. 0 means sold out.")


class ProductSearchResult(BaseModel):
    """One match from search_products: just enough to pick the right product."""

    product_id: str = Field(description="Use this id with the other tools.")
    name: str
    price: float = Field(description="Price in US dollars.")
    in_stock: bool = Field(description="True if at least one size is available.")


class ProductDetails(BaseModel):
    """Full info for one product, from get_product_details."""

    product_id: str
    name: str
    price: float = Field(description="Price in US dollars.")
    description: str
    colors: list[str]
    stock: list[SizeStock] = Field(description="Every size this product comes in, with quantity.")


class ProductNotFound(BaseModel):
    """Returned when no product matches the given id."""

    product_id: str
    found: Literal[False] = False
    message: str


class SizeStockResult(BaseModel):
    """Answer to 'is size X available?' from check_size_stock."""

    product_id: str
    name: str | None = Field(description="Product name, or null if the product wasn't found.")
    size: str = Field(description="The size that was checked, in standard form (XS-XXL).")
    status: Literal["in_stock", "sold_out", "size_not_offered", "product_not_found"]
    quantity: int = Field(description="Units of that size in stock (0 unless status is in_stock).")
    sizes_offered: list[str] = Field(description="All sizes this product comes in.")
    sizes_in_stock: list[str] = Field(description="Sizes with at least 1 unit available right now.")
