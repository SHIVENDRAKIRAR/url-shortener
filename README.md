# Sinly — URL Shortener

A production-style full-stack URL shortener built with **FastAPI, PostgreSQL, Redis, and vanilla JavaScript**.

Sinly supports both **guest and authenticated users**, offering features such as **custom aliases, configurable expiry, analytics, QR generation, caching, rate limiting, and dashboard management**.

Guest users can shorten URLs instantly with **automatic 24-hour expiry**, while authenticated users unlock advanced features such as **custom aliases, analytics, QR generation, soft delete, and dashboard access**.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Redis](https://img.shields.io/badge/Redis-Cache-red)

### 🚀 Live Demo

https://sinly.netlify.app/

### 📚 API Documentation

https://url-shortener-0izm.onrender.com/docs

---

## Features

| Feature             | Guest | Authenticated |
| ------------------- | ----- | ------------- |
| URL shortening      | ✓     | ✓             |
| Automatic expiry    | 24h   | Optional      |
| Custom alias        | ✗     | ✓             |
| Configurable expiry | ✗     | ✓             |
| Dashboard           | ✗     | ✓             |
| Soft delete         | ✗     | ✓             |
| QR generation       | ✗     | ✓             |
| Click analytics     | ✗     | ✓             |

---

## Technical Highlights

- **Redis Cache-Aside Pattern** for low-latency redirects
- **JWT Authentication** with bcrypt password hashing
- **Rate limiting** on public shortening endpoint
- **Lazy expiry validation** without schedulers or cron jobs
- **Soft delete architecture** for preserving analytics
- **User-level URL deduplication** to avoid duplicate shortened URLs
- **Service layer architecture** separating business logic from HTTP concerns
- **Docker Compose** for reproducible local development

---

## Engineering Decisions

**Why Redis Cache-Aside?**  
URL redirects are read-heavy operations. Redis reduces database load and significantly improves response time for frequently accessed links.

**Why Lazy Expiry?**  
Instead of relying on cron jobs or background schedulers, expiry is validated during access, reducing infrastructure complexity.

**Why Soft Delete?**  
Soft deletion preserves analytics integrity while allowing users to remove URLs from active usage.

**Why Service Layer Architecture?**  
Separating business logic from HTTP routes improves maintainability, scalability, and testability.

---

## Architecture

### Project Structure

```
url-shortener/
├── app/
│   ├── core/
│   │   └── config.py          # Centralized settings
│   ├── database/
│   │   └── db.py              # Engine, session, Base
│   ├── models/
│   │   ├── url.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── url.py
│   │   └── user.py
│   ├── routes/
│   │   ├── auth.py            # HTTP layer only
│   │   └── url.py
│   ├── services/
│   │   ├── auth_service.py    # Auth business logic
│   │   └── url_service.py     # URL business logic
│   └── utils/
│       ├── auth.py            # JWT, hashing helpers
│       ├── base62.py          # Short code generation
│       ├── cache.py           # Redis helpers
│       ├── limiter.py         # Rate limiter setup
│       └── logger.py
├── frontend/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### URL Creation Flow

```
POST /shorten
        ↓
Rate Limit Check
        ↓
Request Validation (Pydantic)
        ↓
Guest / Auth Branching
        ↓
Alias & Deduplication Check
        ↓
Short Code Generation (Base62)
        ↓
PostgreSQL Insert
        ↓
Response
```

### Redirect Flow

```
GET /{short_code}
         ↓
Redis Lookup
   ├── HIT  → Validate + Redirect
   └── MISS → PostgreSQL Query
                     ↓
               Cache Result
                     ↓
         Expiry / Delete Validation
                     ↓
          Update Click Analytics
                     ↓
                307 Redirect
```

---

## Tech Stack

| Layer             | Technology                |
| ----------------- | ------------------------- |
| Backend           | FastAPI, Python 3.11      |
| Database          | PostgreSQL (Supabase)     |
| Cache             | Redis (Upstash)           |
| ORM               | SQLAlchemy                |
| Validation        | Pydantic v2               |
| Authentication    | JWT (python-jose), bcrypt |
| Rate Limiting     | slowapi                   |
| Frontend          | HTML, CSS, JavaScript     |
| Deployment        | Render, Netlify           |
| Local Development | Docker Compose            |

---

## API Overview

### Authentication

| Method | Endpoint         | Description       |
| ------ | ---------------- | ----------------- |
| POST   | `/auth/register` | Register account  |
| POST   | `/auth/login`    | Authenticate user |

### URL Management

| Method | Endpoint           | Auth     | Description          |
| ------ | ------------------ | -------- | -------------------- |
| POST   | `/shorten`         | Optional | Create shortened URL |
| GET    | `/{short_code}`    | No       | Redirect to origin   |
| GET    | `/my-urls`         | Yes      | User dashboard       |
| DELETE | `/urls/{id}`       | Yes      | Soft delete URL      |
| GET    | `/urls/{id}/stats` | Yes      | Retrieve analytics   |
| GET    | `/urls/{id}/qr`    | Yes      | Generate QR code     |

### Example Request

```json
{
  "url": "https://example.com",
  "custom_alias": "portfolio",
  "expires_in": 7
}
```

### Example Response

```json
{
  "id": 42,
  "original_url": "https://example.com",
  "short_url": "https://sinly.netlify.app/abc123",
  "click_count": 0,
  "created_at": "2026-06-14T10:00:00",
  "expires_at": "2026-06-21T10:00:00",
  "is_deleted": false,
  "last_visited_at": null,
  "status": "active"
}
```

---

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=
SECRET_KEY=
BASE_URL=
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=
```

---

## Local Setup

### Docker

```bash
git clone https://github.com/SHIVENDRAKIRAR/url-shortener
cd url-shortener
cp .env.example .env
docker compose up --build
```

### Manual

```bash
git clone https://github.com/SHIVENDRAKIRAR/url-shortener
cd url-shortener
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at: http://127.0.0.1:8000/docs

---

## Deployment

| Service  | Purpose             |
| -------- | ------------------- |
| Render   | Backend hosting     |
| Supabase | PostgreSQL database |
| Upstash  | Redis caching       |
| Netlify  | Frontend hosting    |

---

## Future Improvements

- Custom analytics dashboard visualizations
- Background cleanup jobs for expired guest URLs
- User folders/tags for managing links
- Click geo-location analytics
- Custom domain support

---

## License

Built as a production-style backend engineering project focused on system design, caching, authentication, and scalable API architecture.
