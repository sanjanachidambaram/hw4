// Keeps track of which products the logged-in shopper has saved, so every
// heart button on the page shows the right state.
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import * as api from "./api";
import { useAuth } from "./AuthContext";

interface FavoritesState {
  isSaved: (productId: string) => boolean;
  toggle: (productId: string) => void;
}

const FavoritesContext = createContext<FavoritesState | null>(null);

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [saved, setSaved] = useState<Set<string>>(new Set());
  const [notice, setNotice] = useState<"login" | "error" | null>(null);

  // Load this shopper's saved ids whenever someone logs in or out.
  useEffect(() => {
    setSaved(new Set());
    if (!user) return;
    let stale = false;
    api
      .fetchFavorites()
      .then((data) => !stale && setSaved(new Set(data.product_ids)))
      .catch(() => {});
    return () => {
      stale = true;
    };
  }, [user]);

  // Hide the little message after a few seconds.
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(null), 5000);
    return () => clearTimeout(timer);
  }, [notice]);

  const isSaved = useCallback((id: string) => saved.has(id), [saved]);

  const toggle = useCallback(
    (id: string) => {
      if (!user) {
        setNotice("login");
        return;
      }
      const wasSaved = saved.has(id);
      // Update the heart right away, then undo it if the server says no.
      setSaved((prev) => {
        const next = new Set(prev);
        if (wasSaved) next.delete(id);
        else next.add(id);
        return next;
      });
      (wasSaved ? api.removeFavorite(id) : api.addFavorite(id)).catch(() => {
        setSaved((prev) => {
          const next = new Set(prev);
          if (wasSaved) next.add(id);
          else next.delete(id);
          return next;
        });
        setNotice("error");
      });
    },
    [user, saved],
  );

  return (
    <FavoritesContext.Provider value={{ isSaved, toggle }}>
      {children}
      {notice && (
        <div className="toast" role="status">
          <span>
            {notice === "login" ? (
              <>
                ❤️ Want to save this for later?{" "}
                <Link to="/login" onClick={() => setNotice(null)}>
                  Log in
                </Link>{" "}
                to keep your favorites.
              </>
            ) : (
              <>Sorry, we couldn't update your favorites. Please try again.</>
            )}
          </span>
          <button type="button" onClick={() => setNotice(null)} aria-label="Dismiss">
            ×
          </button>
        </div>
      )}
    </FavoritesContext.Provider>
  );
}

export function useFavorites(): FavoritesState {
  const ctx = useContext(FavoritesContext);
  if (!ctx) throw new Error("useFavorites must be used inside <FavoritesProvider>");
  return ctx;
}
