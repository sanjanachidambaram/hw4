# Campus Customs (HW4)

A campus merch shop for the Yale community, with an AI shopping assistant.

- **Front end:** React + Vite + TypeScript (`frontend/`). Shop, product pages, "Find your fit" quiz, favorites, cart, log in / sign up, and a chat box on every page.
- **Back end:** Python FastAPI (`backend/`). Serves products, stock, and images from a SQLite database, handles accounts, and runs the chatbot.
- **Chatbot:** a PydanticAI agent (`backend/agent.py`) using **gpt-5.6-luna** through Portkey, with 5 read-only database tools (`backend/tools.py`) and instructions in `backend/prompts/prompt.md`.

Full write-up: [`output/harness.md`](output/harness.md). Design notes: [`output/design.md`](output/design.md) and [`design rules.md`](design%20rules.md). Every prompt used to build this: [`AI_prompts.md`](AI_prompts.md).

---

## 1. What you need

- **Python 3.12+** (built with 3.13)
- **Node.js 20+** (built with Node 24 LTS)
- **The data pack** (`campus_customs.db` and the `products/` photo folder). It's **not in this repo** because it contains user accounts and the assignment's product photos.
- **A Portkey API key** (only needed for the chatbot; the rest of the site works without it)

## 2. Put the data pack in `data/`

Create a `data` folder inside `hw4` and put the data pack in it, so it looks like this:

```
hw4/
  data/
    campus_customs.db
    products/
      2025-yale-vs-harvard-t-shirt.jpg
      ... (102 product photos)
```

The `data/` folder is in `.gitignore`, so it's never uploaded. The backend adds the extra tables it needs (`chat_messages`, `favorites`) automatically on first start, without changing the existing ones.

## 3. Add your secrets (`.env`)

Copy `.env.example` to `.env` in the `hw4` folder and fill it in:

```
PORTKEY_API_KEY=your-real-portkey-key
SESSION_SECRET=a-long-random-string
COOKIE_SECURE=false
```

Generate a good `SESSION_SECRET` with:

```
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

`.env` is in `.gitignore`, so never commit it or share it.

## 4. One-time setup

**Back end** (from the `hw4` folder):

```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r ..\requirements.txt
```

On macOS/Linux, use `source .venv/bin/activate` instead of `.venv\Scripts\activate`.

**Front end** (from the `hw4` folder, in a second terminal):

```
cd frontend
npm install
```

## 5. Run it

You need **two terminals**, one for each server. Keep both open while you use the site.

**Terminal 1, back end** (port 8000):

```
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Terminal 2, front end** (port 5173):

```
cd frontend
npm run dev
```

Then open **http://localhost:5173**. Use `localhost`, not `127.0.0.1`, so the login cookie works.

**Windows shortcut:** after the one-time setup, you can double-click `start-site.bat` instead. It opens both servers in their own windows and then opens the site.

**Test login:** `test@campuscustoms.yale.edu` / `password`

## 6. Project layout

```
hw4/
  AI_prompts.md          every prompt used to build the project, word for word
  README.md              this file
  requirements.txt       Python packages for the backend
  .env.example           template for your .env (secrets)
  .gitignore             keeps .env, data/, and installed packages out of git
  design rules.md        full design guidelines (colors, fonts, buttons)
  start-site.bat         Windows double-click launcher
  frontend/              Vite + React + TypeScript app
    src/                 pages, components, cart, favorites, chat widget
    public/images/       3 free Unsplash lifestyle photos (see CREDITS.md)
  backend/
    main.py              FastAPI server: products, accounts, favorites, quiz, chat routes
    agent.py             the PydanticAI chatbot (model, instructions, limits, memory)
    tools.py             the 5 read-only tools the chatbot can use
    models.py            Pydantic types for chat requests/replies and tool results
    prompts/prompt.md    the chatbot's instructions and safety rules
    auth.py              password hashing, input checks, rate limits
    history.py           saved chat history for logged-in shoppers
    favorites.py         saved favorites for logged-in shoppers
    catalog.py           groups products into kinds, colors, and price bands
    audit.py             appends every tool call to output/audit_trail.json
  output/
    harness.md           how everything works, specs, and test results
    design.md            short overview of the design changes
    usability.md         the four usability improvements
    app_check.html       site-testing page with screenshots (double-click to open)
    app_check_images/    screenshots used by app_check.html
    audit_trail.json     append-only log of the chatbot's tool calls
  data/                  (not in git) campus_customs.db + products/
```

## Troubleshooting

- **"SESSION_SECRET is missing or too short":** create `.env` from `.env.example` (step 3).
- **Products don't load, or "Is the backend server running?":** start the back end (terminal 1), and check that `data/campus_customs.db` exists.
- **Product images are missing:** make sure the photos are in `data/products/`.
- **The chat says the assistant isn't available:** add `PORTKEY_API_KEY` to `.env` and restart the back end.
