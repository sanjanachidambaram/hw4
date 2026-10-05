// The shopping cart. Kept in this browser (localStorage) so it works for
// guests too. Only product id, size, and quantity are stored; names, prices,
// and stock are always re-read from the backend so they're never out of date.
import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "./AuthContext";

export interface CartLine {
  product_id: string;
  size: string;
  quantity: number;
}

interface CartState {
  lines: CartLine[];
  count: number;
  add: (productId: string, size: string, quantity: number, productName: string) => void;
  setQuantity: (productId: string, size: string, quantity: number) => void;
  remove: (productId: string, size: string) => void;
  clear: () => void;
}

const STORAGE_KEY = "cc_cart";
const MAX_PER_LINE = 10;

const CartContext = createContext<CartState | null>(null);

/** Read the saved cart, ignoring anything malformed. */
function loadCart(): CartLine[] {
  try {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]");
    if (!Array.isArray(data)) return [];
    return data.filter(
      (l): l is CartLine =>
        typeof l?.product_id === "string" &&
        typeof l?.size === "string" &&
        Number.isInteger(l?.quantity) &&
        l.quantity > 0,
    );
  } catch {
    return [];
  }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const [lines, setLines] = useState<CartLine[]>(loadCart);
  const [added, setAdded] = useState<string | null>(null);
  const previousUser = useRef(user);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(lines));
  }, [lines]);

  // Empty the cart when someone logs out, so the next person on a shared
  // computer doesn't see it.
  useEffect(() => {
    if (loading) return;
    if (previousUser.current && !user) setLines([]);
    previousUser.current = user;
  }, [user, loading]);

  useEffect(() => {
    if (!added) return;
    const timer = setTimeout(() => setAdded(null), 4000);
    return () => clearTimeout(timer);
  }, [added]);

  const add = useCallback((productId: string, size: string, quantity: number, productName: string) => {
    setLines((prev) => {
      const existing = prev.find((l) => l.product_id === productId && l.size === size);
      if (existing) {
        return prev.map((l) =>
          l === existing ? { ...l, quantity: Math.min(MAX_PER_LINE, l.quantity + quantity) } : l,
        );
      }
      return [...prev, { product_id: productId, size, quantity: Math.min(MAX_PER_LINE, quantity) }];
    });
    setAdded(`${productName} (${size})`);
  }, []);

  const setQuantity = useCallback((productId: string, size: string, quantity: number) => {
    setLines((prev) =>
      quantity <= 0
        ? prev.filter((l) => !(l.product_id === productId && l.size === size))
        : prev.map((l) =>
            l.product_id === productId && l.size === size
              ? { ...l, quantity: Math.min(MAX_PER_LINE, quantity) }
              : l,
          ),
    );
  }, []);

  const remove = useCallback((productId: string, size: string) => {
    setLines((prev) => prev.filter((l) => !(l.product_id === productId && l.size === size)));
  }, []);

  const clear = useCallback(() => setLines([]), []);

  const count = lines.reduce((sum, l) => sum + l.quantity, 0);

  return (
    <CartContext.Provider value={{ lines, count, add, setQuantity, remove, clear }}>
      {children}
      {added && (
        <div className="toast toast-cart" role="status">
          <span>
            ✓ Added <strong>{added}</strong> to your cart.{" "}
            <Link to="/cart" onClick={() => setAdded(null)}>
              View cart
            </Link>
          </span>
          <button type="button" onClick={() => setAdded(null)} aria-label="Dismiss">
            ×
          </button>
        </div>
      )}
    </CartContext.Provider>
  );
}

export function useCart(): CartState {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used inside <CartProvider>");
  return ctx;
}

export { MAX_PER_LINE };
