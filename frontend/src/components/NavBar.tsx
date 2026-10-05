import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { useCart } from "../CartContext";

const links = [
  { to: "/", label: "Home" },
  { to: "/products", label: "Shop" },
  { to: "/quiz", label: "Find your fit" },
  { to: "/about", label: "About" },
];

export default function NavBar() {
  const { user, loading, logout } = useAuth();
  const { count } = useCart();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <div className="site-header">
      <div className="announce">
        New: find your fit in three clicks. <Link to="/quiz">Take the quiz →</Link>
      </div>
      <header className="navbar">
        <NavLink to="/" className="brand">
          Campus <span>Customs</span>
        </NavLink>
        <nav className="nav-links" aria-label="Main">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} end={link.to === "/"}>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <nav className="nav-account" aria-label="Account">
          {loading ? null : user ? (
            <>
              {/* React shows the name as plain text, so it can't inject code. */}
              <span className="nav-greeting">Hi, {user.first_name}</span>
              <button type="button" className="nav-text-button" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login">Log in</NavLink>
              <NavLink to="/signup" className="nav-signup">
                Create account
              </NavLink>
            </>
          )}
          <NavLink to="/favorites" className="icon-link" aria-label="Favorites" title="Favorites">
            <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
              <path
                d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinejoin="round"
              />
            </svg>
          </NavLink>
          <NavLink
            to="/cart"
            className="icon-link cart-link"
            aria-label={`Cart, ${count} item${count === 1 ? "" : "s"}`}
            title="Cart"
          >
            <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
              <path
                d="M6 7h12l-1 13H7L6 7Zm3 0V6a3 3 0 0 1 6 0v1"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinejoin="round"
              />
            </svg>
            {count > 0 && <span className="cart-badge">{count}</span>}
          </NavLink>
        </nav>
      </header>
    </div>
  );
}
