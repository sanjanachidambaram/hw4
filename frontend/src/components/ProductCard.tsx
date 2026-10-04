import { Link } from "react-router-dom";
import { formatPrice, imageUrl } from "../api";
import type { Product } from "../types";

const SHORT_DESCRIPTION_LENGTH = 90;

function shorten(text: string): string {
  if (text.length <= SHORT_DESCRIPTION_LENGTH) return text;
  return text.slice(0, SHORT_DESCRIPTION_LENGTH).trimEnd() + "…";
}

export default function ProductCard({ product }: { product: Product }) {
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
