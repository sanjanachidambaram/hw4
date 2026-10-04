// Every call to the backend goes through this file, so there's one place
// to change if the backend address changes.
import type { ChatReply, Product, ProductDetail, User } from "./types";

export const API_BASE =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/** Error carrying the backend's message, safe to show to the user. */
export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    // Send the login cookie with every request so the backend knows who you are.
    credentials: "include",
    headers: init.body ? { "Content-Type": "application/json" } : undefined,
  });
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (typeof data.detail === "string") message = data.detail;
    } catch {
      // response wasn't JSON; keep the generic message
    }
    throw new ApiError(res.status, message);
  }
  return res.json() as Promise<T>;
}

function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) });
}

export function fetchProducts(): Promise<Product[]> {
  return request<Product[]>("/api/products");
}

export function fetchProduct(productId: string): Promise<ProductDetail> {
  return request<ProductDetail>(`/api/products/${encodeURIComponent(productId)}`);
}

export function imageUrl(product: Product): string {
  return `${API_BASE}${product.image_url}`;
}

export function sendChatMessage(message: string): Promise<ChatReply> {
  return post<ChatReply>("/api/chat", { message });
}

// ---------- Accounts ----------

export interface SignupData {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

export function signup(data: SignupData): Promise<User> {
  return post<User>("/api/auth/signup", data);
}

export function login(email: string, password: string): Promise<User> {
  return post<User>("/api/auth/login", { email, password });
}

export function logout(): Promise<unknown> {
  return post("/api/auth/logout", {});
}

export async function fetchCurrentUser(): Promise<User | null> {
  const data = await request<{ user: User | null }>("/api/auth/me");
  return data.user;
}

export function formatPrice(price: number): string {
  return `$${price.toFixed(2)}`;
}
