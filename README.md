# Interactive Geo Explorer

An interactive atlas of record-breaking places. Forty-seven locations — eighteen world
landmarks and twenty-nine Indian states and union territories — plotted at their real
coordinates on a Leaflet map, each with a photograph, a record worth knowing about, and a
search guide that answers questions about them and cites the records it used.

## Features

- **The World atlas** — eighteen landmarks across six continents, filterable by continent.
- **The India atlas** — a world record from every state and UT, filterable by region
  (North, South, East, West, Central, Northeast).
- **Real coordinates** — every marker sits at its true latitude/longitude, with a live
  coordinate readout as you move across the map, and a click-to-recentre coordinate line.
- **Search everything** — <kbd>Ctrl</kbd>/<kbd>⌘</kbd> + <kbd>K</kbd> opens a command
  palette over all 47 places; pick one and the app opens the right atlas and flies to it.
- **Keyboard navigation** — arrow keys step through places, <kbd>Esc</kbd> clears the
  selection, and the detail panel has previous/next controls with a running index.
- **Shareable links** — the URL tracks what you're looking at (`#/india/kerala`), so a
  reload or a shared link lands on exactly that place.
- **Detail panel** — photograph, category, decimal coordinates and the full record for
  whichever marker you select.
- **A guide that cites its sources** — ask about any place in your own words and get an
  answer drawn from the records, with chips naming exactly which ones it used; click a chip
  to jump to that place on the map.

## The guide: retrieval, not an API call

The guide is a search engine over the 47 records, written from scratch in the standard
library. There is no API key, no network call, no per-question cost, and nothing to expire.

**How it works.** `src/guide/` builds a TF-IDF vector-space index over every record, with
the title and category weighted above the prose. A question is tokenised, lightly stemmed,
and scored against each record by cosine similarity, then adjusted by two things that
matter more than raw similarity:

- *Coverage* — the share of the question's distinctive weight the record actually accounts
  for. Words the corpus has never seen count against it, which is what stops "the capital
  of France" being answered confidently with the Eiffel Tower entry.
- *Title hits* — naming a place outright should beat merely sharing vocabulary with it.

Questions that are arithmetic rather than lookup are handled before retrieval, in
`src/guide/intents.py`: counts ("how many places are in South India?"), locations and
great-circle distances ("how far is the Eiffel Tower from the Colosseum?"), nearest
neighbours, compass superlatives ("the northernmost place in India"), category listings and
side-by-side comparisons. These are computed from the coordinates, so they are either right
or absent.

**What it can't do.** It is not a language model. It won't reason, summarise across records,
or answer anything the corpus doesn't contain — and when a question goes past what it holds,
it says so and offers the closest entries instead of inventing something. That honesty is
the point: every sentence it returns is quoted from a record or calculated from one, which
is a guarantee no hosted model can make.

Run `pytest` to see both halves pinned: that it finds the right record, and that it declines
what it cannot answer.

## Accounts

Optional, and deliberately not a wall. Everything — both atlases, all 47 records, search,
deep links, the guide — works with no account. Sign-up exists (bcrypt-hashed passwords in
local SQLite, signed http-only session cookie) but nothing is gated behind it.

## The atlas cards and sign-in backdrop

The maps on the home cards aren't images — they're SVG drawn at runtime from real
coastline geometry (Natural Earth's public-domain 110m land data, plus open India state
boundaries), simplified with Douglas–Peucker into `frontend/js/geo-shapes.js`. The dots on
them are the actual places, projected with the same equirectangular maths the outlines use,
so each card is a genuine preview of that atlas's contents rather than stock art.

## Tech stack

| Layer | Choice |
| --- | --- |
| API | FastAPI + Uvicorn |
| Frontend | Vanilla HTML/CSS/JS — no framework, no build step |
| Maps | Leaflet.js (CDN) over OpenStreetMap tiles |
| Auth | SQLite + bcrypt, signed session cookies (`itsdangerous`) |
| Guide | A TF-IDF retriever written from scratch — no external service |

## Running it locally

```bash
pip install -r requirements.txt

cp .env.example .env
# then set the one value in .env:
#   SESSION_SECRET_KEY  python -c "import secrets; print(secrets.token_hex(32))"

uvicorn server.main:app --reload
```

Open <http://127.0.0.1:8000> and pick an atlas — no account needed.
Interactive API docs are at <http://127.0.0.1:8000/api/docs>.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/api/signup` | Create an account |
| `POST` | `/api/login` | Sign in, sets the session cookie |
| `POST` | `/api/logout` | Clear the session |
| `GET` | `/api/me` | Current user, or 401 |
| `GET` | `/api/places/world` | The eighteen world landmarks — public |
| `GET` | `/api/places/india` | The twenty-nine states and UTs — public |
| `POST` | `/api/chat` | Ask the local guide; returns an answer plus its citations |

## Project structure

```
server/           FastAPI app — routers, schemas, session dependency
  routers/          auth, places, chat
src/
  auth/             SQLite connection + bcrypt signup/login
  data/             GeoPlace records with real coordinates
  guide/            TF-IDF index, intent handlers, answer composer
frontend/
  index.html        single-page shell
  css/styles.css    the whole visual system
  js/
    app.js            view router, deep links, boot
    api.js            fetch wrappers for every endpoint
    auth.js           sign in / create account
    map.js            Leaflet, markers, filters, selection
    palette.js        Ctrl-K search over all 47 places
    plot.js           renders the SVG atlas previews
    chat.js           the guide panel
    geo-shapes.js     generated coastline path data
  images/           landmark and state photographs
legacy/           earlier versions of this project (see below)
```

## Notes on two decisions

**Tiles.** The map uses standard OpenStreetMap tiles with a CSS filter applied to the tile
pane to darken them. CartoDB's dark basemaps — the obvious choice — now require an API key
and render "API KEY REQUIRED" watermarks without one; every other genuinely dark tile style
(Stadia, Thunderforest, MapTiler) also sits behind a signup. OSM standard tiles stay free
and keyless, so the dark treatment is done in CSS instead.

**No CORS.** The frontend is served by the same FastAPI app that serves the API, so there is
no cross-origin boundary and no CORS middleware.

## Project history

This is the third iteration of the same idea, and the earlier two are kept in `legacy/`:

1. **`legacy/pythonproject.py`** — the original Tkinter desktop app with a MySQL backend.
   Detected map clicks by matching mouse coordinates against hardcoded pixel rectangles,
   which broke on any screen resolution other than the one they were measured on. Stored
   passwords in plaintext.
2. **`legacy/streamlit_app/`** — a Streamlit + Folium rewrite. Fixed both of those problems
   (real coordinates, bcrypt hashing) but was limited by Streamlit's rerun-per-interaction
   model and its widget styling.
3. **This version** — a FastAPI JSON API with a hand-built frontend, for full control over
   the interface.

## Requirements

- Python 3.10+
- Nothing else: no API keys, no external services
