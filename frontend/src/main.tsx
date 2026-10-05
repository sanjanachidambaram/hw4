import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./AuthContext";
import { FavoritesProvider } from "./FavoritesContext";
import { CartProvider } from "./CartContext";
// Free fonts bundled with the site (no outside font server).
import "@fontsource-variable/fraunces";
import "@fontsource-variable/inter";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <FavoritesProvider>
          <CartProvider>
            <App />
          </CartProvider>
        </FavoritesProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);
