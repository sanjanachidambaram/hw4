import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProducts } from "../api";
import ProductCard from "../components/ProductCard";
import type { Product } from "../types";

const FEATURED_COUNT = 4;

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
      <section className="hero">
        <h1>Wear where you belong.</h1>
        <p>
          Campus Customs makes gear for everyone who calls Yale home: students
          pulling late nights, alumni coming back for The Game, and families
          cheering from the stands. From residential college crewnecks to
          varsity hoodies, find the piece that says where you're from.
        </p>
        <Link to="/products" className="button-link large">
          Shop the collection
        </Link>
      </section>

      <section className="highlights">
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
        <section>
          <h2>Fresh picks</h2>
          <div className="product-grid">
            {featured.map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
          </div>
        </section>
      )}
    </>
  );
}
