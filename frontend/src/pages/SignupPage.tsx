import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { ApiError } from "../api";
import { useAuth } from "../AuthContext";

const MIN_PASSWORD_LENGTH = 8; // matches backend/auth.py

export default function SignupPage() {
  const { user, signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    confirm: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const update = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    // Quick checks before bothering the server. The backend checks all of
    // these again, since anyone can skip the browser and call it directly.
    if (!form.first_name.trim() || !form.last_name.trim() || !form.email.trim()) {
      setError("Please fill in every field.");
      return;
    }
    if (form.password.length < MIN_PASSWORD_LENGTH) {
      setError(`Password must be at least ${MIN_PASSWORD_LENGTH} characters.`);
      return;
    }
    if (form.password !== form.confirm) {
      setError("Passwords don't match.");
      return;
    }

    setSubmitting(true);
    try {
      await signup({
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        password: form.password,
      });
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="auth-card">
      <h1>Create account</h1>
      <form onSubmit={handleSubmit} noValidate>
        <div className="form-row">
          <label>
            First name
            <input autoComplete="given-name" value={form.first_name} onChange={update("first_name")} maxLength={50} required />
          </label>
          <label>
            Last name
            <input autoComplete="family-name" value={form.last_name} onChange={update("last_name")} maxLength={50} required />
          </label>
        </div>
        <label>
          Email
          <input type="email" autoComplete="email" value={form.email} onChange={update("email")} maxLength={254} required />
        </label>
        <label>
          Password
          <input type="password" autoComplete="new-password" value={form.password} onChange={update("password")} maxLength={128} required />
          <span className="hint">At least {MIN_PASSWORD_LENGTH} characters. Avoid common passwords.</span>
        </label>
        <label>
          Confirm password
          <input type="password" autoComplete="new-password" value={form.confirm} onChange={update("confirm")} maxLength={128} required />
        </label>
        {form.confirm && form.password !== form.confirm && (
          <p className="hint warn">Passwords don't match yet.</p>
        )}
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" disabled={submitting}>
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>
      <p className="muted">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </section>
  );
}
