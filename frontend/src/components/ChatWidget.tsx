import { useEffect, useRef, useState, type FormEvent } from "react";
import { matchPath, useLocation } from "react-router-dom";
import { ApiError, fetchChatHistory, sendChatMessage, type PageInfo } from "../api";
import { useAuth } from "../AuthContext";
import type { CardProduct } from "../types";
import ProductCard from "./ProductCard";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  products?: CardProduct[];
}

const MAX_MESSAGE_LENGTH = 1000; // matches the limit in backend/models.py
const GREETING: ChatMessage = {
  role: "assistant",
  content: "Hi! I'm the Campus Customs assistant. Ask me about any product, price, or size.",
};

export default function ChatWidget() {
  const { user } = useAuth();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  // When someone logs in or out, reset the chat so the next person on this
  // computer never sees the previous person's messages. A logged-in shopper
  // then gets their own saved history from the server; a guest starts fresh.
  useEffect(() => {
    setMessages([GREETING]);
    if (!user) return;
    let stale = false; // ignore the answer if the user changes again first
    fetchChatHistory()
      .then((saved) => {
        if (stale || saved.length === 0) return;
        setMessages([
          GREETING,
          ...saved.map((m) => ({ role: m.role, content: m.reply, products: m.products })),
        ]);
      })
      .catch(() => {
        // If history can't load, the chat still works; it just starts fresh.
      });
    return () => {
      stale = true;
    };
  }, [user]);

  // The page the shopper is on right now, sent with every message so the
  // assistant knows what "this" means on a product page.
  function currentPage(): PageInfo {
    const match = matchPath("/products/:productId", location.pathname);
    return { path: location.pathname, product_id: match?.params.productId ?? null };
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    try {
      const { reply, products } = await sendChatMessage(text, currentPage());
      setMessages((prev) => [...prev, { role: "assistant", content: reply, products }]);
    } catch (err) {
      const content =
        err instanceof ApiError
          ? err.message
          : "Sorry, I couldn't reach the server. Please try again.";
      setMessages((prev) => [...prev, { role: "assistant", content }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="chat">
      {open && (
        <section className="chat-panel" aria-label="Chat with Campus Customs">
          <header className="chat-header">
            <span>Campus Customs Chat</span>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </header>
          <div className="chat-messages">
            {messages.map((m, i) => (
              // React renders this as plain text, so a message can't inject HTML.
              <div key={i} className={`chat-bubble ${m.role}`}>
                {m.content}
                {/* Only draw the grid if there's at least one checked card. */}
                {m.products && m.products.length > 0 && (
                  <div className="chat-cards">
                    {m.products.map((p) => (
                      // Same card as the Products page, so clicking opens the detail page.
                      <ProductCard key={p.product_id} product={p} />
                    ))}
                  </div>
                )}
              </div>
            ))}
            {sending && <div className="chat-bubble assistant">…</div>}
            <div ref={bottomRef} />
          </div>
          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about our merch…"
              maxLength={MAX_MESSAGE_LENGTH}
              aria-label="Chat message"
            />
            <button type="submit" disabled={sending || !input.trim()}>
              Send
            </button>
          </form>
        </section>
      )}
      <button
        type="button"
        className="chat-toggle"
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Close chat" : "Open chat"}
      >
        {open ? "×" : "💬"}
      </button>
    </div>
  );
}
