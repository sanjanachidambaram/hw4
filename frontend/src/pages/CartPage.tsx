import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProduct, formatPrice, imageUrl } from "../api";
import { MAX_PER_LINE, useCart } from "../CartContext";
import type { ProductDetail } from "../types";

export default function CartPage() {
  const { lines, setQuantity, remove, count } = useCart();
  // Fresh product info (name, price, stock) for everything in the cart.
  const [details, setDetails] = useState<Record<string, ProductDetail | "missing">>({});
  const [showCheckoutNote, setShowCheckoutNote] = useState(false);

  useEffect(() => {
    const needed = [...new Set(lines.map((l) => l.product_id))].filter((id) => !(id in details));
    needed.forEach((id) =>
      fetchProduct(id)
        .then((p) => setDetails((d) => ({ ...d, [id]: p })))
        .catch(() => setDetails((d) => ({ ...d, [id]: "missing" }))),
    );
  }, [lines, details]);

  if (lines.length === 0) {
    return (
      <section className="cart-page">
        <h1>Your cart</h1>
        <div className="empty-state">
          <p>Your cart is empty. Let's fix that.</p>
          <Link to="/products" className="btn-primary">
            Shop all products
          </Link>
        </div>
      </section>
    );
  }

  const rows = lines.map((line) => {
    const product = details[line.product_id];
    const stock =
      product && product !== "missing"
        ? product.inventory.find((s) => s.size === line.size)?.quantity ?? 0
        : null;
    return { line, product, stock };
  });
  const subtotal = rows.reduce(
    (sum, r) => (r.product && r.product !== "missing" ? sum + r.product.price * r.line.quantity : sum),
    0,
  );
  const loading = rows.some((r) => !r.product);
  const problems = rows.filter((r) => r.product === "missing" || (r.stock !== null && r.line.quantity > r.stock));

  return (
    <section className="cart-page">
      <h1>Your cart</h1>
      <p className="muted">
        {count} item{count === 1 ? "" : "s"}
      </p>
      <div className="cart-layout">
        <ul className="cart-lines">
          {rows.map(({ line, product, stock }) => (
            <li key={`${line.product_id}-${line.size}`} className="cart-line">
              {!product ? (
                <p className="muted">Loading…</p>
              ) : product === "missing" ? (
                <>
                  <p className="error">This item is no longer available.</p>
                  <button type="button" className="link-button" onClick={() => remove(line.product_id, line.size)}>
                    Remove
                  </button>
                </>
              ) : (
                <>
                  <Link to={`/products/${product.product_id}`} className="cart-thumb">
                    <img src={imageUrl(product)} alt={product.name} />
                  </Link>
                  <div className="cart-info">
                    <Link to={`/products/${product.product_id}`} className="cart-name">
                      {product.name}
                    </Link>
                    <p className="muted">
                      Size {line.size} · {formatPrice(product.price)} each
                    </p>
                    {stock === 0 ? (
                      <p className="sold-out">Size {line.size} just sold out. Please remove it.</p>
                    ) : stock !== null && line.quantity > stock ? (
                      <p className="sold-out">Only {stock} left in {line.size}.</p>
                    ) : null}
                    <div className="cart-controls">
                      <div className="qty-stepper">
                        <button
                          type="button"
                          aria-label={`Fewer ${product.name}`}
                          onClick={() => setQuantity(line.product_id, line.size, line.quantity - 1)}
                        >
                          −
                        </button>
                        <span>{line.quantity}</span>
                        <button
                          type="button"
                          aria-label={`More ${product.name}`}
                          disabled={line.quantity >= Math.min(MAX_PER_LINE, stock ?? 0)}
                          onClick={() => setQuantity(line.product_id, line.size, line.quantity + 1)}
                        >
                          +
                        </button>
                      </div>
                      <button type="button" className="link-button" onClick={() => remove(line.product_id, line.size)}>
                        Remove
                      </button>
                    </div>
                  </div>
                  <p className="cart-line-total">{formatPrice(product.price * line.quantity)}</p>
                </>
              )}
            </li>
          ))}
        </ul>

        <aside className="cart-summary">
          <h2>Order summary</h2>
          <div className="summary-row">
            <span>Subtotal</span>
            <strong>{loading ? "…" : formatPrice(subtotal)}</strong>
          </div>
          <p className="muted small">Shipping and taxes are calculated at checkout.</p>
          <button
            type="button"
            className="btn-cart btn-block"
            disabled={loading || problems.length > 0}
            onClick={() => setShowCheckoutNote(true)}
          >
            Checkout
          </button>
          {problems.length > 0 && <p className="hint warn">Fix the items marked above to check out.</p>}
          {showCheckoutNote && (
            <p className="checkout-note">
              Thanks! Checkout isn't part of this class project yet, so no order was placed and no payment was taken.
            </p>
          )}
          <Link to="/products" className="link-button">
            ← Keep shopping
          </Link>
        </aside>
      </div>
    </section>
  );
}
