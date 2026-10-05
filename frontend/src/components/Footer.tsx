import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <p className="footer-logo">Campus Customs</p>
          <p>Gear for everyone who calls Yale home. Students, alumni, families, and fans.</p>
        </div>
        <nav aria-label="Shop">
          <p className="footer-heading">Shop</p>
          <Link to="/products">All products</Link>
          <Link to="/products?kind=Hoodies">Hoodies</Link>
          <Link to="/products?kind=Crewnecks">Crewnecks</Link>
          <Link to="/products?kind=T-shirts">T-shirts</Link>
        </nav>
        <nav aria-label="Help">
          <p className="footer-heading">Help</p>
          <Link to="/quiz">Find your fit quiz</Link>
          <Link to="/favorites">Your favorites</Link>
          <Link to="/cart">Your cart</Link>
          <span className="footer-note">Questions? Use the chat in the corner.</span>
        </nav>
        <nav aria-label="Company">
          <p className="footer-heading">Campus Customs</p>
          <Link to="/about">About us</Link>
          <Link to="/login">Log in</Link>
          <Link to="/signup">Create account</Link>
        </nav>
      </div>
      <div className="footer-bottom">
        <span>© 2026 Campus Customs · New Haven, CT</span>
        <span>Lifestyle photos via Unsplash</span>
      </div>
    </footer>
  );
}
