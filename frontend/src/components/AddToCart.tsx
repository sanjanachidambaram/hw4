// "Add to cart" for one product. On the product page it shows size buttons
// right away; on a product card it opens a small size picker first.
import { useState } from "react";
import { fetchProduct } from "../api";
import { MAX_PER_LINE, useCart } from "../CartContext";
import type { SizeStock } from "../types";

/** Size buttons + Add to cart, used on the product page and inside the card picker. */
export function SizePicker({
  productId,
  productName,
  sizes,
  onAdded,
  compact = false,
}: {
  productId: string;
  productName: string;
  sizes: SizeStock[];
  onAdded?: () => void;
  compact?: boolean;
}) {
  const { add, lines } = useCart();
  const [size, setSize] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);

  const inCart = (s: string) =>
    lines.find((l) => l.product_id === productId && l.size === s)?.quantity ?? 0;
  const available = sizes.filter((s) => s.quantity > 0);
  const chosen = sizes.find((s) => s.size === size);
  // Never let someone add more than we have (or more than 10 at once).
  const maxQty = chosen ? Math.max(0, Math.min(MAX_PER_LINE, chosen.quantity) - inCart(chosen.size)) : 0;

  if (available.length === 0) {
    return <p className="sold-out">Sold out in every size</p>;
  }

  return (
    <div className={`size-picker ${compact ? "compact" : ""}`}>
      {!compact && <p className="size-label">Size</p>}
      <div className="size-options" role="group" aria-label="Choose a size">
        {sizes.map((s) => (
          <button
            key={s.size}
            type="button"
            className={`size-option ${size === s.size ? "selected" : ""}`}
            disabled={s.quantity === 0}
            aria-pressed={size === s.size}
            title={s.quantity === 0 ? "Sold out" : `${s.quantity} in stock`}
            onClick={() => {
              setSize(s.size);
              setQuantity(1);
            }}
          >
            {s.size}
          </button>
        ))}
      </div>
      {!compact && chosen && (
        <div className="qty-row">
          <span className="size-label">Quantity</span>
          <div className="qty-stepper">
            <button type="button" aria-label="Fewer" onClick={() => setQuantity((q) => Math.max(1, q - 1))} disabled={quantity <= 1}>
              −
            </button>
            <span aria-live="polite">{quantity}</span>
            <button type="button" aria-label="More" onClick={() => setQuantity((q) => Math.min(maxQty, q + 1))} disabled={quantity >= maxQty}>
              +
            </button>
          </div>
        </div>
      )}
      {chosen && maxQty === 0 && (
        <p className="hint">You already have all available {chosen.size}s in your cart.</p>
      )}
      <button
        type="button"
        className="btn-cart"
        disabled={!chosen || maxQty === 0}
        onClick={() => {
          if (!chosen) return;
          add(productId, chosen.size, Math.min(quantity, maxQty), productName);
          setSize(null);
          setQuantity(1);
          onAdded?.();
        }}
      >
        {chosen ? "Add to cart" : "Select a size"}
      </button>
    </div>
  );
}

/** The card version: a button that loads sizes and opens the picker. */
export function CardAddToCart({ productId, productName }: { productId: string; productName: string }) {
  const [open, setOpen] = useState(false);
  const [sizes, setSizes] = useState<SizeStock[] | null>(null);
  const [error, setError] = useState(false);

  function openPicker() {
    setOpen(true);
    if (sizes) return;
    fetchProduct(productId)
      .then((p) => setSizes(p.inventory))
      .catch(() => setError(true));
  }

  if (!open) {
    return (
      <button type="button" className="btn-cart btn-card-cart" onClick={openPicker}>
        Add to cart
      </button>
    );
  }
  return (
    <div className="card-cart-panel">
      <div className="card-cart-head">
        <span>Choose a size</span>
        <button type="button" className="link-button" onClick={() => setOpen(false)} aria-label="Close size picker">
          ×
        </button>
      </div>
      {error ? (
        <p className="error">Couldn't load sizes. Try again.</p>
      ) : !sizes ? (
        <p className="muted">Loading sizes…</p>
      ) : (
        <SizePicker productId={productId} productName={productName} sizes={sizes} onAdded={() => setOpen(false)} compact />
      )}
    </div>
  );
}
