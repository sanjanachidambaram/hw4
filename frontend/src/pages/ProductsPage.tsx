import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { fetchProducts, fetchQuizResults } from "../api";
import ProductCard from "../components/ProductCard";
import type { CardProduct } from "../types";

// The same 6 kinds the quiz uses (backend/catalog.py).
const KINDS = ["Hoodies", "Crewnecks", "T-shirts", "Quarter-zips", "Jackets & fleece", "Long-sleeve shirts"];

export default function ProductsPage() {
  const [params, setParams] = useSearchParams();
  const kind = KINDS.includes(params.get("kind") ?? "") ? (params.get("kind") as string) : null;
  const [products, setProducts] = useState<CardProduct[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setProducts(null);
    setError(null);
    // "All" uses the full catalogue; a kind reuses the quiz's database filter.
    const load = kind
      ? fetchQuizResults({ kind, color: "any", budget: "any" })
      : fetchProducts();
    load
      .then(setProducts)
      .catch(() => setError("We couldn't load products. Is the backend server running?"));
  }, [kind]);

  return (
    <>
      <div className="section-head">
        <p className="eyebrow">The collection</p>
        <h1>{kind ?? "All products"}</h1>
      </div>
      <div className="filter-chips" role="group" aria-label="Filter by kind">
        <button
          type="button"
          className={`chip ${kind === null ? "active" : ""}`}
          aria-pressed={kind === null}
          onClick={() => setParams({})}
        >
          All
        </button>
        {KINDS.map((k) => (
          <button
            key={k}
            type="button"
            className={`chip ${kind === k ? "active" : ""}`}
            aria-pressed={kind === k}
            onClick={() => setParams({ kind: k })}
          >
            {k}
          </button>
        ))}
      </div>
      {error ? (
        <p className="error">{error}</p>
      ) : !products ? (
        <p className="muted">Loading products…</p>
      ) : (
        <>
          <p className="muted result-count">{products.length} items</p>
          <div className="product-grid">
            {products.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        </>
      )}
    </>
  );
}
