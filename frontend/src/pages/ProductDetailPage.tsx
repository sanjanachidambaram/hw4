import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchProduct, formatPrice, imageUrl } from "../api";
import type { ProductDetail } from "../types";
import HeartButton from "../components/HeartButton";

const LOW_STOCK = 5;

function stockLabel(quantity: number): string {
  if (quantity === 0) return "Sold out";
  if (quantity < LOW_STOCK) return `Only ${quantity} left`;
  return `${quantity} in stock`;
}

export default function ProductDetailPage() {
  const { productId } = useParams();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!productId) return;
    setProduct(null);
    setError(null);
    fetchProduct(productId)
      .then(setProduct)
      .catch(() => setError("Sorry, we couldn't find that product."));
  }, [productId]);

  if (error)
    return (
      <>
        <p className="error">{error}</p>
        <Link to="/products">← Back to all products</Link>
      </>
    );
  if (!product) return <p className="muted">Loading…</p>;

  return (
    <>
      <Link to="/products" className="back-link">
        ← Back to all products
      </Link>
      <div className="product-detail">
        <img src={imageUrl(product)} alt={product.name} />
        <div>
          <p className="muted">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <div className="price-row">
            <p className="price large">{formatPrice(product.price)}</p>
            <HeartButton productId={product.product_id} productName={product.name} className="detail-heart" />
          </div>
          <p>{product.description}</p>
          <p>
            <strong>Colors:</strong> {product.colors.join(", ")}
          </p>

          <h2>Sizes &amp; stock</h2>
          {product.inventory.length === 0 ? (
            <p className="muted">Size information isn't available.</p>
          ) : (
            <table className="stock-table">
              <tbody>
                {product.inventory.map((s) => (
                  <tr key={s.size} className={s.quantity === 0 ? "sold-out" : ""}>
                    <td>{s.size}</td>
                    <td>{stockLabel(s.quantity)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}
