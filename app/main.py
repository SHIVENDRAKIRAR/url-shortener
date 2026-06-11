from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.database.db import engine
from app.models.url import Base
from app.routes.auth import router as auth_router
from app.routes.url import router as url_router
from app.utils.limiter import limiter

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="Shorten URLs with analytics, expiry, custom aliases and QR codes.",
    version="1.0.0",
)

# Middleware — must be registered before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(auth_router)
app.include_router(url_router)  # last — catches /{short_code}


@app.get("/", tags=["health"])
def home():
    return {"status": "ok", "message": "URL Shortener API is running"}