import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProducts } from "../api";
import ProductCard from "../components/ProductCard";
import type { Product } from "../types";

const FEATURED_COUNT = 4;

// Real kinds of item in the catalogue (same groups as the quiz).
const KINDS = [
  { kind: "Hoodies", blurb: "Pullovers & full-zips" },
  { kind: "Crewnecks", blurb: "College & team classics" },
  { kind: "T-shirts", blurb: "Everyday tees" },
  { kind: "Quarter-zips", blurb: "Smart layers" },
  { kind: "Jackets & fleece", blurb: "Cold-weather warmth" },
];

export default function HomePage() {
  const [featured, setFeatured] = useState<Product[]>([]);

  useEffect(() => {
    fetchProducts()
      .then((products) =>
        setFeatured(products.filter((p) => p.total_stock > 0).slice(0, FEATURED_COUNT)),
      )
      .catch(() => setFeatured([]));
  }, []);

  return (
    <>
      <section className="hero full-bleed">
        <div className="hero-inner">
          <p className="eyebrow eyebrow-light">New Haven's campus shop</p>
          <h1>Wear where you belong.</h1>
          <p className="hero-text">
            Campus Customs makes gear for everyone who calls Yale home: students pulling late
            nights, alumni coming back for The Game, and families cheering from the stands.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn-primary">
              Shop the collection
            </Link>
            <Link to="/quiz" className="btn-outline-light">
              Find your fit
            </Link>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-head">
          <p className="eyebrow">Shop by kind</p>
          <h2>Find your favorite layer</h2>
        </div>
        <div className="kind-tiles">
          {KINDS.map((k) => (
            <Link key={k.kind} to={`/products?kind=${encodeURIComponent(k.kind)}`} className="kind-tile">
              <span className="kind-name">{k.kind}</span>
              <span className="kind-blurb">{k.blurb}</span>
              <span className="kind-arrow" aria-hidden="true">
                →
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section className="value-row">
        <div>
          <h3>Your college, your colors</h3>
          <p>Crewnecks, quarter-zips, and fleeces for residential colleges and schools.</p>
        </div>
        <div>
          <h3>Game day ready</h3>
          <p>Team tees, hoodies, and rivalry classics for the sideline.</p>
        </div>
        <div>
          <h3>Gifts for the whole family</h3>
          <p>Mom, Dad, Grandpa, cousin: everyone gets to rep the Bulldogs.</p>
        </div>
      </section>

      {featured.length > 0 && (
        <section className="section">
          <div className="section-head section-head-row">
            <div>
              <p className="eyebrow">Fresh picks</p>
              <h2>In stock and ready to wear</h2>
            </div>
            <Link to="/products" className="text-link">
              View all products →
            </Link>
          </div>
          <div className="product-grid">
            {featured.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        </section>
      )}

      <section className="promo-band full-bleed">
        <div className="promo-inner">
          <p className="eyebrow">Not sure where to start?</p>
          <h2>Three questions. Your perfect pick.</h2>
          <p>Tell us what you like and your budget, and we'll narrow 100+ items down to a few.</p>
          <Link to="/quiz" className="btn-primary">
            Take the quiz
          </Link>
        </div>
      </section>
    </>
  );
}
