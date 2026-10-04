import { useEffect, useRef, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { ApiError, formatPrice, sendChatMessage } from "../api";
import { useAuth } from "../AuthContext";
import type { ChatReply } from "../types";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  products?: ChatReply["products"];
}

const MAX_MESSAGE_LENGTH = 1000; // matches the limit in backend/models.py
const GREETING: ChatMessage = {
  role: "assistant",
  content: "Hi! I'm the Campus Customs assistant. Ask me about any product, price, or size.",
};

export default function ChatWidget() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open]);

  // Start a fresh conversation when someone logs in or out, so the next
  // person on this computer doesn't see the previous person's chat.
  useEffect(() => {
    setMessages([GREETING]);
  }, [user]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    try {
      const { reply, products } = await sendChatMessage(text);
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
                {m.products && m.products.length > 0 && (
                  <div className="chat-products">
                    {m.products.map((p) => (
                      <Link key={p.product_id} to={`/products/${p.product_id}`}>
                        {p.name} · {formatPrice(p.price)}
                      </Link>
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
