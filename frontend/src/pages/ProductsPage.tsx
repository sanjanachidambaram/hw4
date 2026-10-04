import { useEffect, useState } from "react";
import { fetchProducts } from "../api";
import ProductCard from "../components/ProductCard";
import type { Product } from "../types";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch(() =>
        setError("We couldn't load products. Is the backend server running?"),
      );
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!products) return <p className="muted">Loading products…</p>;

  return (
    <>
      <h1>All products</h1>
      <p className="muted">{products.length} items</p>
      <div className="product-grid">
        {products.map((p) => (
          <ProductCard key={p.product_id} product={p} />
        ))}
      </div>
    </>
  );
}
