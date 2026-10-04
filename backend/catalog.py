"""Simple, consistent groupings of the catalogue, built from the real data.

The catalogue's garment_type column has 22 slightly different labels
("short-sleeve T-shirt", "t-shirt", "pullover hoodie", "hoodie", ...).
These helpers sort them into the 6 kinds of item the shop actually sells,
and group the garments' main colors and prices. They're used by the quiz
and by the chatbot's similar-items tool. The database itself is not changed.
"""

import json

# The 6 kinds of item in the catalogue (checked against all 102 products).
CATEGORIES = ["T-shirts", "Crewnecks", "Hoodies", "Quarter-zips", "Jackets & fleece", "Long-sleeve shirts"]

# How to say "a ___" for each kind, used in short explanations.
SINGULAR = {
    "T-shirts": "a T-shirt",
    "Crewnecks": "a crewneck",
    "Hoodies": "a hoodie",
    "Quarter-zips": "a quarter-zip",
    "Jackets & fleece": "a jacket or fleece",
    "Long-sleeve shirts": "a long-sleeve shirt",
}

# Main garment colors, grouped. (Reds, golds, and blacks only appear as logo
# colors, never as the garment's main color, so they're not offered.)
COLOR_FAMILIES = ["Navy & blue", "Gray", "White & cream"]

# Price bands that line up with the shop's real prices ($32-$98).
BUDGETS = {
    "Under $50": (0, 50),
    "$50 to $75": (50, 75),
    "Over $75": (75, 10_000),
}


def category_of(garment_type: str) -> str:
    """Map a raw garment_type label to one of CATEGORIES."""
    g = garment_type.lower()
    if "t-shirt" in g:
        return "T-shirts"
    if "hood" in g:
        return "Hoodies"
    if "quarter-zip" in g:
        return "Quarter-zips"
    if "jacket" in g:
        return "Jackets & fleece"
    if "long-sleeve" in g:
        return "Long-sleeve shirts"
    return "Crewnecks"  # crewneck, raglan crewneck, mockneck sweatshirt


def color_family(color: str) -> str | None:
    """Map one color name to a family in COLOR_FAMILIES, or None."""
    c = color.lower()
    if "navy" in c or "blue" in c:
        return "Navy & blue"
    if "gray" in c or "grey" in c or "charcoal" in c:
        return "Gray"
    if c in ("white", "cream", "ivory"):
        return "White & cream"
    return None


def main_color_family(colors_json: str) -> str | None:
    """The family of the garment's main color (the first color listed)."""
    colors = json.loads(colors_json)
    return color_family(colors[0]) if colors else None


def budget_of(price: float) -> str:
    for label, (low, high) in BUDGETS.items():
        if low <= price < high:
            return label
    return "Over $75"
