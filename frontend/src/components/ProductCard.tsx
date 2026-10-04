import { Link } from "react-router-dom";
import { formatPrice, imageUrl } from "../api";
import type { CardProduct } from "../types";

const SHORT_DESCRIPTION_LENGTH = 90;

function shorten(text: string): string {
  if (text.length <= SHORT_DESCRIPTION_LENGTH) return text;
  return text.slice(0, SHORT_DESCRIPTION_LENGTH).trimEnd() + "…";
}

// Each card is a real link (<a href="/products/...">), and React handles its
// clicks at the page root, so cards added later (e.g. by the chat) open the
// detail page exactly like cards that were there when the page loaded.
export default function ProductCard({ product }: { product: CardProduct }) {
  return (
    <Link to={`/products/${product.product_id}`} className="product-card">
      <img src={imageUrl(product)} alt={product.name} loading="lazy" />
      <div className="product-card-body">
        <h3>{product.name}</h3>
        <p className="price">{formatPrice(product.price)}</p>
        <p className="muted">{shorten(product.description)}</p>
        {product.total_stock === 0 && <p className="sold-out">Sold out</p>}
      </div>
    </Link>
  );
}
