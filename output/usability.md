# Campus Customs: Usability Improvements

Four improvements to make shopping easier: two on the website, and two that make the chatbot smarter.

---

## 1. Favorites ❤️

**What I added:** A heart button on every product card and on each product's own page. Logged-in shoppers click the heart to save an item (the heart fills in) and click again to un-save it. A new **Favorites** page shows everything they've saved, newest first, using the same product cards as the rest of the shop. Un-saving an item on that page removes it right away. If nothing is saved yet, the page says so and links to the Products page.

**Why it helps:** Shoppers often browse before they buy, like comparing a few hoodies or picking a gift for a parent. Favorites let them build a short list instead of hunting for items again later. For the business, saved items show what people are interested in, and they bring shoppers back.

**Where to find it:** The heart is on every product card (Products page, Home page, Favorites page, and cards in the chat) and next to the price on a product's page. The **Favorites** link is in the top nav bar. If you're not logged in and click a heart, a friendly message pops up in the bottom-left corner with a **Log in** link (nothing is saved, and nothing breaks). Logged-out visitors who open the Favorites page see a note inviting them to log in or create an account.

---

## 2. "Find your fit" quiz 🧭

**What I added:** A short quiz with three button questions, built from what's actually in the catalogue:
- **What are you looking for?** T-shirts, Crewnecks, Hoodies, Quarter-zips, Jackets & fleece, Long-sleeve shirts, or Surprise me.
- **Pick a color:** Navy & blue, Gray, White & cream, or No preference. These are the garments' main colors; other colors only appear in logos.
- **What's your budget?** Under $50, $50 to $75, Over $75, or Any price.

It then shows the matching products from the catalogue as product cards (with hearts), in-stock items first, then cheapest first. Each answer button shows how many items match so far, and buttons that would lead to zero results are greyed out. If nothing matches, there's a friendly message and a **Start over** button. A **Back** button lets shoppers change an earlier answer.

**Why it helps:** With 102 products, a new shopper or a visiting parent can feel overwhelmed. The quiz gets them to a handful of good picks in three clicks. It's free to run, since it filters the catalogue directly and doesn't use the AI.

**Where to find it:** The **Quiz** link in the top nav bar.

---

## 3. Similar items (chatbot) 🔄

**What I added:** A new chatbot tool that finds in-stock alternatives to a product: the same kind of item, a close price, and a matching color when possible. It returns up to 4 suggestions, each with a short reason built from the data (for example "also a hoodie; same price; also navy blue"). If the shopper needs a particular size, it only suggests items with that size in stock.

**Why it helps:** When a hoodie is sold out in someone's size, the bot can offer a close alternative instead of a dead end. That keeps the shopper happy and keeps the sale.

**Where to find it:** In the chat (bottom-right corner). Ask "anything like this?" or "something similar?". On a product page, "this" means the product you're looking at. The bot also offers alternatives on its own when an item or size is sold out.

---

## 4. Compare (chatbot) ⚖️

**What I added:** A new chatbot tool that lines up two or three products side by side: name, kind of item, price, description, colors, and which sizes are in stock or sold out. The tool only returns facts from the database. The chatbot explains the differences in friendly words, without adding anything that isn't in the data.

**Why it helps:** "What's the difference between the Champion hoodie and the basic one?" is a common shopping question. A clear side-by-side answer helps people decide quickly and confidently.

**Where to find it:** In the chat. Ask things like "what's the difference between X and Y?", "compare these two", or "which is cheaper?". If the bot can't find one of the products, it says so instead of guessing.

---

## Tested and working

- **Favorites:** a guest click shows the log-in message. When logged in, save, un-save, the Favorites page, the product-page heart, and the empty message all work, and each person only sees their own favorites.
- **Quiz:** all three questions work. Hoodies + Navy & blue + $50 to $75 gives 15 picks, which matches the database. Dead-end answers are greyed out, and the no-results message and Start over work.
- **Similar items:** on the Baseball Left Chest Crewneck page, "Do you have this in XS? If not, anything similar?" gave: XS is sold out, plus 4 crewnecks with XS in stock, all $58.
- **Compare:** the Basic Hoodie vs. Champion Reverse Weave Hoodie answer matched the database (same $68 price; the Champion is sold out in XS and XL). Asking to compare with a "Harvard Crimson Hoodie" got an honest "couldn't find that product."
