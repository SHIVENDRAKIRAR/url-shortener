# Sinly — URL Shortener

A production-style full-stack URL shortener built with **FastAPI, PostgreSQL, Redis, and vanilla JavaScript**.

Supports guest and authenticated users with features such as **custom aliases, configurable expiry, analytics, QR generation, caching, and rate limiting**.

**Live Demo:** https://sinly.netlify.app/
**API Documentation:** https://url-shortener-0izm.onrender.com/docs

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

* **Redis Cache-Aside Pattern** for low-latency redirects
* **JWT Authentication** with bcrypt password hashing
* **Rate limiting** on public shortening endpoint
* **Lazy expiry validation** without schedulers or cron jobs
* **Soft delete architecture** for preserving analytics
* **URL deduplication** to prevent duplicate records
* **Docker Compose** for reproducible local development

---

## Architecture

### URL Creation Flow

```text
Client Request
    ↓
POST /shorten
    ↓
Rate Limit Check
    ↓
Request Validation
    ↓
Deduplication Check
    ↓
Short Code Generation
    ↓
PostgreSQL Insert
    ↓
Response
```

### Redirect Flow

```text
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
       Update Analytics
                    ↓
              307 Redirect
```

---

## Tech Stack

| Layer             | Technology                  |
| ----------------- | --------------------------- |
| Backend           | FastAPI, Python 3.11        |
| Database          | PostgreSQL (Supabase)       |
| Cache             | Redis (Upstash)             |
| ORM               | SQLAlchemy                  |
| Validation        | Pydantic v2                 |
| Authentication    | JWT (`python-jose`), bcrypt |
| Rate Limiting     | slowapi                     |
| Frontend          | HTML, CSS, JavaScript       |
| Deployment        | Render, Netlify             |
| Local Development | Docker Compose              |

---

## API Overview

### Authentication

| Method | Endpoint         | Description       |
| ------ | ---------------- | ----------------- |
| POST   | `/auth/register` | Register account  |
| POST   | `/auth/login`    | Authenticate user |

### URL Management

| Method | Endpoint           | Auth     | Description              |
| ------ | ------------------ | -------- | ------------------------ |
| POST   | `/shorten`         | Optional | Create shortened URL     |
| GET    | `/{short_code}`    | No       | Redirect to original URL |
| GET    | `/my-urls`         | Yes      | User dashboard           |
| DELETE | `/urls/{id}`       | Yes      | Soft delete URL          |
| GET    | `/urls/{id}/stats` | Yes      | Retrieve analytics       |
| GET    | `/urls/{id}/qr`    | Yes      | Generate QR code         |

### Example Request

```json
{
  "url": "https://example.com",
  "custom_alias": "portfolio",
  "expires_in": 7
}
```

---

## Project Structure

```text
url-shortener/
├── app/
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   └── utils/
│
├── frontend/
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
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

### Manual Setup

```bash
git clone https://github.com/SHIVENDRAKIRAR/url-shortener
cd url-shortener

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at:

```text
http://127.0.0.1:8000/docs
```

---

## Deployment

| Service  | Purpose             |
| -------- | ------------------- |
| Render   | Backend hosting     |
| Supabase | PostgreSQL database |
| Upstash  | Redis caching       |
| Netlify  | Frontend hosting    |

---

## License

Built for learning and portfolio purposes.
