import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchFavorites } from "../api";
import { useAuth } from "../AuthContext";
import ProductCard from "../components/ProductCard";
import { useFavorites } from "../FavoritesContext";
import type { CardProduct } from "../types";

export default function FavoritesPage() {
  const { user, loading } = useAuth();
  const { isSaved } = useFavorites();
  const [products, setProducts] = useState<CardProduct[] | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!user) return;
    setProducts(null);
    fetchFavorites()
      .then((data) => setProducts(data.products))
      .catch(() => setError(true));
  }, [user]);

  if (loading) return <p className="muted">Loading…</p>;

  if (!user) {
    return (
      <article className="prose">
        <h1>Your favorites</h1>
        <p>
          <Link to="/login">Log in</Link> to save items you love and find them here later. New here?{" "}
          <Link to="/signup">Create an account</Link>.
        </p>
      </article>
    );
  }

  if (error) return <p className="error">We couldn't load your favorites. Please try again.</p>;
  if (!products) return <p className="muted">Loading your favorites…</p>;

  // Hide items un-saved on this page right away, without reloading.
  const visible = products.filter((p) => isSaved(p.product_id));

  return (
    <>
      <h1>Your favorites</h1>
      {visible.length === 0 ? (
        <div className="empty-state">
          <p>You haven't saved anything yet. Tap the ♡ on any product to save it here.</p>
          <Link to="/products" className="button-link large">
            Browse products
          </Link>
        </div>
      ) : (
        <>
          <p className="muted">
            {visible.length} saved item{visible.length === 1 ? "" : "s"}
          </p>
          <div className="product-grid">
            {visible.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        </>
      )}
    </>
  );
}
