import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";

const links = [
  { to: "/", label: "Home" },
  { to: "/products", label: "Products" },
  { to: "/about", label: "About Us" },
];

export default function NavBar() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <header className="navbar">
      <NavLink to="/" className="brand">
        Campus Customs
      </NavLink>
      <nav className="nav-links">
        {links.map((link) => (
          <NavLink key={link.to} to={link.to} end={link.to === "/"}>
            {link.label}
          </NavLink>
        ))}
      </nav>
      <nav className="nav-account">
        {loading ? null : user ? (
          <>
            {/* React shows the name as plain text, so it can't inject code. */}
            <span className="nav-greeting">Hi, {user.first_name}</span>
            <button type="button" className="button-link" onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login">Log in</NavLink>
            <NavLink to="/signup" className="button-link">
              Create account
            </NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
