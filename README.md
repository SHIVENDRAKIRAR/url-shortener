# URL Shortener API

A production-ready URL shortener backend built with FastAPI and PostgreSQL. Features JWT authentication, Redis caching, rate limiting, and full Docker support.

**Live API:** https://url-shortener-0izm.onrender.com/docs

---

## Features

- Shorten URLs with random 5-character Base62 codes
- Redirect with click tracking
- User accounts with JWT authentication
- Per-user URL deduplication — same URL always returns the same short code
- Redis caching for fast redirects (Cache-Aside pattern)
- Rate limiting on `/shorten` (5 requests/minute per IP)
- Delete your own URLs
- Paginated URL listing
- Per-URL analytics (click count, created date)
- Structured logging
- Fully Dockerized local development

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11 + FastAPI |
| Database | PostgreSQL + SQLAlchemy ORM |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt |
| Cache | Redis (Upstash in production) |
| Rate Limiting | slowapi |
| Deployment | Render + Supabase + Upstash |
| Local Dev | Docker Compose |

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | None | Health check |
| POST | `/auth/register` | None | Create account |
| POST | `/auth/login` | None | Login → JWT token |
| POST | `/shorten` | JWT | Shorten a URL (5/min limit) |
| GET | `/my-urls` | JWT | List your URLs (paginated) |
| GET | `/urls/{id}/stats` | JWT | Click count + analytics |
| DELETE | `/urls/{id}` | JWT | Delete a URL |
| GET | `/{short_code}` | None | Redirect to original URL |

---

## Local Setup

### Without Docker

```bash
# Clone the repo
git clone https://github.com/SHIVENDRAKIRAR/url-shortener
cd url-shortener

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your values (see Environment Variables section)

# Run the server
uvicorn app.main:app --reload
```

API available at: http://127.0.0.1:8000/docs

### With Docker

```bash
# Clone the repo
git clone https://github.com/SHIVENDRAKIRAR/url-shortener
cd url-shortener

# Create .env file and fill in values
cp .env.example .env

# Start all services (app + postgres + redis)
docker compose up --build
```

API available at: http://localhost:8000/docs

---

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
SECRET_KEY=your_secret_key_here
BASE_URL=http://localhost:8000
UPSTASH_REDIS_REST_URL=https://your-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token_here
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Project Structure

```
url-shortener/
├── app/
│   ├── main.py              # App entry point
│   ├── database/
│   │   └── db.py            # DB engine + session
│   ├── models/
│   │   ├── url.py           # URLs table
│   │   └── user.py          # Users table
│   ├── routes/
│   │   ├── url.py           # URL endpoints
│   │   └── auth.py          # Auth endpoints
│   ├── schemas/
│   │   ├── url.py           # URL request/response schemas
│   │   └── user.py          # User request/response schemas
│   └── utils/
│       ├── auth.py          # JWT + bcrypt helpers
│       ├── base62.py        # Random short code generator
│       ├── cache.py         # Redis cache helpers
│       ├── limiter.py       # Rate limiter instance
│       └── logger.py        # Structured logging
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## How It Works

### URL Shortening
Each URL gets a random 5-character Base62 code (a-z, A-Z, 0-9 = 916M+ combinations). If the same user shortens the same URL again, the existing short code is returned instead of creating a new one.

### Redirect Flow
```
Request → Check Redis cache
              ↓
         Cache HIT → Redirect immediately (no DB)
         Cache MISS → Query PostgreSQL → Cache result → Redirect
```

### Authentication
Login returns a JWT token (30 min expiry). Pass it as `Authorization: Bearer <token>` header on protected routes.

---

## Deployment

Deployed on:
- **App**: [Render](https://render.com) — auto-deploys on every push to main
- **Database**: [Supabase](https://supabase.com) — managed PostgreSQL
- **Cache**: [Upstash](https://upstash.com) — serverless Redis
