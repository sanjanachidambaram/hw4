import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <article className="prose">
      <h1>Page not found</h1>
      <p>
        That page doesn't exist. <Link to="/">Head back home</Link>.
      </p>
    </article>
  );
}
