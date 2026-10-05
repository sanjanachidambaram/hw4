# Campus Customs: Usability Improvements

I made the following improvements to make shopping easier:.

---

## 1. Favorites ❤️

**What I added:** A heart button on every product card and on each product's own page, which can be used like a general / generic like button. Logged-in shoppers can heart and save product cards to the Favorites section. The heart is on every single product card and the Favorites link is in the top navigation bar.

**Why it helps:** This allows shoppers to remember and compare the items they like -- this way, if they're browsing on their phone before they buy, they can look at their laptop and view their saved items before. This works for other use cases as well.

---

## 2. "Find your fit" quiz 🧭

**What I added:** A short quiz with three button questions, built from what's actually in the catalogue:
- **What are you looking for?** T-shirts, Crewnecks, Hoodies, Quarter-zips, Jackets & fleece, Long-sleeve shirts, or Surprise me.
- **Pick a color:** Navy & blue, Gray, White & cream, or No preference. These are the garments' main colors; other colors only appear in logos.
- **What's your budget?** Under $50, $50 to $75, Over $75, or Any price.

Then, it shows matching products. This is located in the Quiz link in the navigation bar.

**Why it helps:** This fun quiz allows shoppers to quickly and easily see exactly what picks are perfect for them. The filter works on the catalogue directly and doesn't use AI, so it's free! 102 products, a new shopper or a visiting parent can feel overwhelmed. The quiz gets them to a handful of good picks in three clicks. It's free to run, since it filters the catalogue directly and doesn't use the AI.

---

## 3. Similar items (chatbot) 🔄

**What I added:** A new chatbot feature that finds in-stock alternatives to a product: the same kind of item, a close price, and a matching color when possible, returning up to four suggestions.

**Why it helps:** When a hoodie is sold out in someone's size, the bot can offer a close alternative instead of a dead end. For example, if you say, "I want a L Boola Boola t shirt," the chatbot now suggests other similar items, since it is out of stock.

---

## 4. Compare (chatbot) ⚖️

**What I added:** A new chatbot feature that lines up products side by side and compares them, using facts from the database.

**Why it helps:** Shoppers can find a quick and easy answer to differentiate similar products. For example, asking, "What's the difference between the Champion hoodie and the basic one?" will return a clear description of how one has a simpler design, slightly different wording, etc.

---

## Tested and working

- **Favorites:** a guest click shows the log-in message. When logged in, save, un-save, the Favorites page, the product-page heart, and the empty message all work, and each person only sees their own favorites.
- **Quiz:** all three questions work. Hoodies + Navy & blue + $50 to $75 gives 15 picks, which matches the database. Dead-end answers are greyed out, and the no-results message and Start over work.
- **Similar items:** on the Baseball Left Chest Crewneck page, "Do you have this in XS? If not, anything similar?" gave: XS is sold out, plus 4 crewnecks with XS in stock, all $58.
- **Compare:** the Basic Hoodie vs. Champion Reverse Weave Hoodie answer matched the database (same $68 price; the Champion is sold out in XS and XL). Asking to compare with a "Harvard Crimson Hoodie" got an honest "couldn't find that product."
