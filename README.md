# URL Shortener

A full-stack URL shortener built with **FastAPI** and **PostgreSQL**. Supports guest usage, authenticated users, custom aliases, link expiry, click analytics, QR code generation, and Redis caching — deployed live on Render.

🔗 **Live API:** https://url-shortener-0izm.onrender.com/docs  

---

## Features

| Feature | Guest | Logged In |
|---|---|---|
| Shorten any URL | ✅ | ✅ |
| Auto 24h expiry | ✅ | — |
| Custom alias | ❌ | ✅ |
| Custom expiry (1/7/30 days or never) | ❌ | ✅ |
| Link dashboard | ❌ | ✅ |
| Delete links (soft delete) | ❌ | ✅ |
| QR code generation | ❌ | ✅ |
| Click analytics | ❌ | ✅ |

**Backend**
- Rate limiting (5 requests/min on `/shorten`)
- Redis caching for fast redirects (Cache-Aside pattern)
- URL deduplication — same URL returns existing short code
- Lazy expiry validation — no scheduler needed
- Structured logging (cache HIT/MISS, auth events)
- Docker Compose for local development

**Frontend**
- Light/dark mode (persists across sessions)
- Guest shorten with no login required
- Dashboard with stats, pagination, copy, QR modal
- Friendly error messages for all failure cases

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL (Supabase) |
| Cache | Redis (Upstash, HTTP/REST) |
| Auth | JWT (python-jose), bcrypt |
| Rate Limiting | slowapi |
| ORM | SQLAlchemy + Pydantic v2 |
| Hosting | Render |
| Local Dev | Docker Compose |
| Frontend | HTML, CSS, Vanilla JS |

---

## API Reference

### Auth

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | None | Create account |
| POST | `/auth/login` | None | Returns JWT token |

### URLs

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/shorten` | Optional | Shorten a URL |
| GET | `/{short_code}` | None | Redirect to original URL |
| GET | `/my-urls` | JWT | Paginated list of user's links |
| DELETE | `/urls/{id}` | JWT | Soft delete a link |
| GET | `/urls/{id}/stats` | JWT | Click count, timestamps |
| GET | `/urls/{id}/qr` | JWT | Returns QR code as PNG |

### POST `/shorten` — Request Body

```json
{
  "url": "https://example.com",
  "custom_alias": "my-link",   // optional, logged-in only
  "expires_in": 7              // optional days: 1, 7, 30 — logged-in only
}
```

Guest requests auto-expire in 24 hours. Logged-in users get never-expiring links by default.

---

## Architecture

```
Client
  │
  ├── POST /shorten
  │     └── slowapi rate limit (5/min by IP)
  │           └── create URL row in PostgreSQL
  │
  └── GET /{short_code}
        ├── Check Upstash Redis (Cache HIT → redirect immediately)
        └── Cache MISS → query PostgreSQL → store in Redis → redirect
```

**Redirect flow in detail:**
1. Request hits `/{short_code}`
2. Redis checked first — if HIT, still validates expiry/deleted from DB
3. If MISS, query DB, store result in Redis (TTL: 1 hour)
4. Check `is_deleted` → 404 if true
5. Check `expires_at` → 410 Gone if expired, clear Redis key
6. Increment `click_count`, update `last_visited_at`
7. Return 307 redirect

---

## Local Setup

### Option 1: Docker Compose (recommended)

```bash
git clone https://github.com/SHIVENDRAKIRAR/url-shortener
cd url-shortener
cp .env.example .env   # fill in your values
docker compose up --build
```

### Option 2: Manual

**Prerequisites:** Python 3.11, PostgreSQL

```bash
git clone https://github.com/SHIVENDRAKIRAR/url-shortener
cd url-shortener
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://user:password@host:port/dbname
SECRET_KEY=your-secret-key-here
BASE_URL=http://127.0.0.1:8000
UPSTASH_REDIS_REST_URL=https://your-upstash-url
UPSTASH_REDIS_REST_TOKEN=your-upstash-token
```

Run:

```bash
uvicorn app.main:app --reload
```

API docs available at: http://127.0.0.1:8000/docs

### Frontend

```bash
cd frontend
# open index.html directly in browser
# set BASE_URL in api.js to http://127.0.0.1:8000
```

---

## Database Schema

```sql
-- users
id            SERIAL PRIMARY KEY
email         VARCHAR UNIQUE NOT NULL
hashed_password VARCHAR NOT NULL
created_at    TIMESTAMPTZ DEFAULT NOW()

-- urls
id            SERIAL PRIMARY KEY
original_url  VARCHAR NOT NULL
short_code    VARCHAR UNIQUE
custom_alias  VARCHAR(50) UNIQUE
user_id       INTEGER REFERENCES users(id)   -- NULL for guests
click_count   INTEGER DEFAULT 0
is_deleted    BOOLEAN DEFAULT FALSE
expires_at    TIMESTAMPTZ                     -- NULL = never expire
last_visited_at TIMESTAMPTZ
created_at    TIMESTAMPTZ DEFAULT NOW()
```

---

## Deployment

Deployed on **Render** (app) + **Supabase** (PostgreSQL) + **Upstash** (Redis).

| Service | Purpose | Free Tier |
|---|---|---|
| Render | FastAPI app hosting | 750 hrs/month |
| Supabase | Managed PostgreSQL | 500MB storage |
| Upstash | Serverless Redis | 10,000 cmds/day |

**Render config:**
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Env vars set in Render dashboard

---

## Project Structure

```
url-shortener/
├── app/
│   ├── main.py              # FastAPI app, middleware, routers
│   ├── database/
│   │   └── db.py            # SQLAlchemy session
│   ├── models/
│   │   ├── url.py           # URL model
│   │   └── user.py          # User model
│   ├── routes/
│   │   ├── auth.py          # Register, login
│   │   └── url.py           # Shorten, redirect, dashboard, QR
│   ├── schemas/
│   │   ├── url.py           # Pydantic request/response models
│   │   └── user.py
│   └── utils/
│       ├── auth.py          # JWT, bcrypt, get_current_user
│       ├── base62.py        # Short code generator
│       ├── cache.py         # Upstash Redis helpers
│       ├── limiter.py       # slowapi instance
│       └── logger.py        # Structured logging
├── frontend/
│   ├── index.html           # Landing + shorten
│   ├── login.html           # Login + register
│   ├── dashboard.html       # Link management
│   ├── style.css            # Light/dark theme
│   ├── api.js               # Fetch wrapper
│   └── app.js               # Shared utilities
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```