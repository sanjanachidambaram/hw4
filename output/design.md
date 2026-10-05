# Campus Customs: Design Guidelines

The feel we're going for: **a classy campus shop with athletic energy.** Think of the confident type and clean product grids of Adidas, and the warm, lived-in feel of Abercrombie, but in navy, white, and a touch of varsity gold. It should look polished and trustworthy, never stiff or corporate. We don't copy any other store's layout or images, and we use **no Yale logos** (the only Yale branding is what's already on the real product photos).

---

## Color palette

Blue and white stay the base, per the project's AGENTS.md. Gold is the one accent, saved for actions like buttons and badges.

| Role | Name | Hex | Used for |
|---|---|---|---|
| Main | **Ink navy** | `#0E1B3D` | Header, footer, headings, main text |
| Supporting blue | **Bulldog blue** | `#1F4FB8` | Links, selected states, small highlights |
| Accent | **Varsity gold** | `#E8B33A` | Add to cart and other main buttons, cart badge, little "eyebrow" labels |
| Accent (hover) | **Deep gold** | `#D19A1C` | Button hover |
| Background | **Paper** | `#FAF8F4` | Page background (a warm off-white, softer than pure white) |
| Surface | **White** | `#FFFFFF` | Cards, forms, panels |
| Lines | **Stone** | `#E6E1D6` | Borders and dividers |
| Soft text | **Slate** | `#5A6175` | Descriptions, helper text |
| Alerts | **Brick** | `#B42318` | Sold out, errors |

**Readability rules:**
- Navy text on Paper or White (15.9:1 and 16.9:1 contrast).
- Navy text on gold buttons (8.8:1; 6.7:1 on hover). Never white text on gold, which is only 1.9:1 and too faint.
- White text on navy (16.9:1).
- Slate is only for secondary text, and it still passes the accessibility standard (5.8:1 on Paper, 6.2:1 on White). The standard asks for at least 4.5:1.

## Fonts (free, bundled with the site so no outside font service tracks visitors)

- **Fraunces** (headings): a warm, slightly old-school serif with real personality. It gives the "established campus shop" feel without being stuffy.
- **Inter** (everything else): a clean, very readable sans for body text, prices, buttons, and forms.
- Small uppercase "eyebrow" labels above section titles (Inter, bold, wide letter spacing) add a sporty touch.

## Spacing

- A simple 8-pixel rhythm: 4, 8, 12, 16, 24, 32, 48, 72.
- Pages max out at about 1,200 pixels wide, with generous white space between sections (48–72 px).
- Inside cards and panels: 16–24 px.

## Buttons

| Type | Look | Used for |
|---|---|---|
| **Primary (gold)** | Gold background, navy bold text, small uppercase lettering, slightly rounded corners (6 px). On hover it darkens, lifts 1 px, and gets a soft shadow | Add to cart, Checkout, Shop now |
| **Secondary (outline)** | Navy outline, navy text, fills navy on hover | Browse, Start over, Back |
| **Text link** | Bulldog blue, underline on hover | Remove, Keep shopping |

Every button gets a visible focus ring for keyboard users.

## Cards

- White card, thin Stone border, 10 px rounded corners, no heavy shadows.
- The product photo sits on a soft off-white tile in a square frame. On hover the photo zooms in slightly and the card lifts a little.
- Name in Inter semi-bold, price in bold navy, short description in Slate.
- A heart in the photo's top-right corner, and a full-width gold **Add to cart** button at the bottom.

## Pages

- **Header:** a slim navy announcement bar on top, then a sticky white header with the wordmark in Fraunces, nav links, and the cart bag with a gold count badge.
- **Hero sections:** a full-width photo with a navy gradient, so the white headline stays readable, plus one gold button and one outline button.
- **Section headings:** an eyebrow label, a Fraunces title, and a short sentence.
- **Footer:** navy, in columns (Shop, Help, About), with plenty of breathing room.

---

## Planned improvements

1. Bundle the **Fraunces + Inter** fonts and switch the whole site over.
2. Put the **palette into shared color settings** (CSS variables) and use them everywhere: pages, cards, forms, quiz, cart, and chat.
3. Add an **announcement bar** and a cleaner **sticky header** with a polished cart icon.
4. Add a **full-width hero photo** on the Home page with a strong headline and two buttons.
5. Add a **"Shop by kind" section** on Home with clean category tiles that point shoppers somewhere useful.
6. Restyle the **product cards**: photo hover zoom, cleaner text, and a **bold gold Add to cart button** with a hover effect.
7. Restyle the **product page**: a bigger photo, a clear price, nicer size buttons, and a prominent gold Add to cart.
8. Add a **photo and value cards to About Us**.
9. Restyle the **cart, quiz, favorites, login/sign-up, and chat** to match.
10. Add a new **footer**.
11. Add **free-to-use stock photos** (hero and About), stored with the site, with their sources and licenses listed here. The real product photos stay on every product card.
12. Check **readability (contrast) and keyboard focus** across the site.

---

## What I actually changed

### First: shopping cart (new feature)
- **What:** A gold **Add to cart** button on every product card (all 102), in the chat's cards, and on each product page. On a card, it opens a small size picker. On the product page, there are size buttons (sold-out sizes are crossed out and can't be picked), a quantity stepper, and a big Add to cart button. A bag icon in the header shows a gold count badge and opens the **Cart** page. There you can change quantities, remove items, see the subtotal, and press Checkout.
  - **Why:** You can't buy what you can't put in a bag. Clear size choices and an always-visible cart count make buying feel easy and safe.
  - **Where:** Every product card, every product page, and the bag icon (top right) → `/cart`.
- **Behind the scenes:** The cart is saved in the browser, so it works for guests and survives a page refresh. It only remembers product, size, and quantity. Names, prices, and stock are always re-checked live, and you can't add more than what's in stock (max 10 per line). Logging out empties the cart, for privacy on shared computers. Checkout shows a friendly "demo only, no order placed" note, since payment isn't part of this project.

### Look and feel
- **Fonts:** Switched from Times New Roman to **Fraunces** (headings) and **Inter** (everything else). Both are free and bundled with the site, so no outside font service sees visitors.
  - **Why:** Fraunces gives the shop a warm, established personality, and Inter keeps prices, buttons, and descriptions easy to read.
  - **Where:** Everywhere.
- **Colors:** Applied the palette everywhere through shared color settings: ink navy, bulldog blue, varsity gold, warm "paper" background, white cards. Every text and background pair was checked with a contrast calculator, and all pass the accessibility standard (navy on gold is 8.8:1).
  - **Why:** A consistent, calm palette looks trustworthy, and readable text keeps people from bouncing.
  - **Where:** Everywhere.
- **Buttons:** Main actions (Add to cart, Checkout, Shop the collection, Take the quiz) are **bold gold with navy uppercase text**. On hover they darken, lift slightly, and glow. Secondary actions use a navy outline.
  - **Why:** One loud color for "do this" makes the next step obvious, which helps people buy.
  - **Where:** All pages.

### Header and footer
- **Announcement bar:** a slim navy strip on top: "New: find your fit in three clicks. Take the quiz →".
  - **Why:** Points first-time visitors to the fastest way to find something.
  - **Where:** Top of every page.
- **New header:** a "Campus *Customs*" wordmark, cleaner links (Home, Shop, Find your fit, About), a gold underline on the current page, and heart (Favorites) and bag (Cart) icons. It stays pinned at the top while you scroll.
  - **Why:** Looks like a real store, and the cart is always one click away.
  - **Where:** Every page.
- **New footer:** navy with columns for Shop, Help, and Campus Customs, plus a photo credit.
  - **Why:** Gives people somewhere to go when they reach the bottom, instead of a dead end.
  - **Where:** Bottom of every page.

### Home page
- **Hero photo:** a full-width photo of a collegiate stone building in fall colors, with a navy fade so the big white headline is easy to read, plus "Shop the collection" (gold) and "Find your fit" (outline) buttons.
  - **Why:** A strong first impression sets the mood and tells shoppers where to click.
  - **Where:** Top of Home.
- **"Shop by kind" tiles:** Hoodies, Crewnecks, T-shirts, Quarter-zips, and Jackets & fleece. On hover, a gold bar slides in and the arrow nudges.
  - **Why:** Most shoppers know what *kind* of thing they want, and this gets them there in one click.
  - **Where:** Home, below the hero. Each tile opens the Shop page already filtered.
- **Value strip, "Fresh picks" grid, and a quiz promo band** with a soft knit-sweater photo behind it.
  - **Why:** Gives the page rhythm and several natural places to start shopping.
  - **Where:** Home.

### Shop and product pages
- **Filter chips on the Shop page:** All, Hoodies, Crewnecks, T-shirts, Quarter-zips, Jackets & fleece, Long-sleeve shirts. These use the same database filter as the quiz, with no AI.
  - **Why:** 102 products is a lot to scroll, and filtering makes browsing fast.
  - **Where:** Shop (`/products`). Links like `/products?kind=Hoodies` work too.
- **Product cards:** photos sit on a soft tile and zoom in a little on hover, the card lifts, the text is cleaner, the heart is in the corner, and there's a full-width gold Add to cart button. **The real product photos are unchanged.**
  - **Why:** A tidy, consistent grid feels premium, and small motion makes it feel alive without being flashy.
  - **Where:** Shop, Home, Favorites, Quiz results, and the chat.
- **Product page:** a big photo, a small category label, a large serif name, a bold price, size buttons, quantity, and the gold Add to cart. The details column stays in view while you scroll.
  - **Why:** Everything needed to decide and buy is in one place, above the fold.
  - **Where:** Click any product.

### Other pages
- **About Us:** a two-column layout with the story beside a warm photo of stacked sweaters, plus three value cards with gold tops.
  - **Why:** A human, friendly story builds trust.
  - **Where:** About.
- **Quiz, Favorites, Cart, Log in / Create account, and Chat:** all restyled with the same fonts, colors, cards, and buttons. The quiz choices lift on hover. The chat has a navy header with a gold underline, navy/white chat bubbles, and a gold Send button.
  - **Why:** Consistency everywhere makes the whole site feel like one trustworthy brand.
  - **Where:** Those pages, and the chat button in the bottom-right corner.

### Accessibility and polish
- Gold keyboard focus rings on everything clickable. Respects "reduce motion" settings. Fixed a sideways-scroll glitch. Layouts stack neatly on phones and tablets.
- Sold-out sizes are crossed out with a striped pattern, so color isn't the only signal.

### Stock photos (free to use)
All three are from **Unsplash** under the free Unsplash License (commercial use allowed, credit appreciated): https://unsplash.com/license. They're saved in `frontend/public/images/` with credits in `CREDITS.md`, so they load fast and no third party sees visitors. I rejected the first candidates because the clothing showed other brands' logos. None of the photos include Yale logos.

| Where | File | Photographer |
|---|---|---|
| Home hero | `hero-campus.jpg` | note thanun |
| About Us | `about-sweaters.jpg` | Storiès |
| Home quiz band (soft background) | `knit-texture.jpg` | Ruta Gudeliene |
