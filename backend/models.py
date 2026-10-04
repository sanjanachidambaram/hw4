"""Pydantic types for the chat (what it sends and gets back) and for what
the chatbot's tools return."""

from typing import Literal

from pydantic import BaseModel, Field

MAX_MESSAGE_LENGTH = 1000


# ---------- Chat request / response ----------

class PageInfo(BaseModel):
    """Which page the shopper is on, sent by the chat box with each message."""

    path: str = Field(default="/", max_length=200)
    # Only lowercase letters, digits, and hyphens, which is how product ids look.
    product_id: str | None = Field(default=None, max_length=100, pattern=r"^[a-z0-9-]+$")


class ChatRequest(BaseModel):
    """What the chat box sends to POST /api/chat."""

    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)
    page: PageInfo | None = None


class ChatHistoryMessage(BaseModel):
    """One saved message, for showing a returning shopper their history."""

    role: Literal["user", "assistant"]
    content: str
    products: list["ChatProductCard"] = Field(default_factory=list)


class ChatHistoryResponse(BaseModel):
    """What GET /api/chat/history returns. Always empty for guests."""

    messages: list[ChatHistoryMessage]


class ChatProductCard(BaseModel):
    """Everything the chat box needs to draw one product card."""

    product_id: str
    name: str
    price: float
    description: str
    image_url: str
    total_stock: int


class ChatResponse(BaseModel):
    """What POST /api/chat sends back to the chat box."""

    reply: str
    products: list[ChatProductCard] = Field(
        default_factory=list,
        description="Product cards to show under the reply. Empty means text only.",
    )


class AgentReply(BaseModel):
    """What the AI itself must return: its chatty text plus which products to show.

    The AI only picks product ids. The server fills in the real card details
    from the database, so the AI can't invent a product, price, or image.
    """

    reply: str = Field(description="Your friendly answer to the customer, in plain text.")
    product_ids: list[str] = Field(
        default_factory=list,
        description=(
            "product_id values from this turn's tool results that the customer should "
            "see as cards. Empty list if no products are relevant."
        ),
    )


# ---------- Tool results ----------

class SizeStock(BaseModel):
    """How many of one size are in stock."""

    size: str = Field(description="Size label, e.g. 'M' or 'XXL'.")
    quantity: int = Field(description="Units in stock. 0 means sold out.")


class CatalogueMatch(BaseModel):
    """One match from search_catalogue: just enough to pick the right products."""

    product_id: str = Field(description="Use this id with the other tools and in product_ids.")
    name: str
    category: str = Field(description="Kind of item, e.g. 'pullover hoodie'.")
    colors: list[str] = Field(description="Colors this product comes in.")
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


class SimilarItem(BaseModel):
    """One in-stock alternative from find_similar_products."""

    product_id: str
    name: str
    price: float = Field(description="Price in US dollars.")
    colors: list[str]
    reason: str = Field(description="Short, factual reason it's similar, built from the data.")


class SimilarItemsResult(BaseModel):
    """Alternatives to one product. `items` is empty if nothing similar is in stock."""

    for_product_id: str
    for_product_name: str
    size: str | None = Field(description="The size the alternatives were checked for, if any.")
    items: list[SimilarItem]


class ComparedProduct(BaseModel):
    """One product's facts, for a side-by-side comparison."""

    product_id: str
    name: str
    kind: str = Field(description="Broad kind of item, e.g. 'Hoodies'.")
    price: float = Field(description="Price in US dollars.")
    description: str
    colors: list[str]
    sizes_in_stock: list[str]
    sizes_sold_out: list[str]


class ComparisonResult(BaseModel):
    """Side-by-side facts for 2-3 products, plus any ids that weren't found."""

    products: list[ComparedProduct]
    not_found: list[str] = Field(description="Requested product_ids that don't exist.")
    note: str | None = Field(default=None, description="Set if the request couldn't be fully handled.")
