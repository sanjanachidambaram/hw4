import { useFavorites } from "../FavoritesContext";

/** Save / un-save a product. A filled heart means it's in Favorites. */
export default function HeartButton({
  productId,
  productName,
  className = "",
}: {
  productId: string;
  productName: string;
  className?: string;
}) {
  const { isSaved, toggle } = useFavorites();
  const saved = isSaved(productId);
  return (
    <button
      type="button"
      className={`heart-button ${saved ? "saved" : ""} ${className}`}
      aria-pressed={saved}
      aria-label={saved ? `Remove ${productName} from favorites` : `Save ${productName} to favorites`}
      title={saved ? "Saved to favorites" : "Save to favorites"}
      onClick={() => toggle(productId)}
    >
      {saved ? "♥" : "♡"}
    </button>
  );
}
