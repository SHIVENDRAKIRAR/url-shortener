from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from app.database.db import engine , Base
from app.routes.auth import router as auth_router
from app.routes.url import router as url_router
from app.utils.limiter import limiter

load_dotenv() # Only load .env in local dev; in production env vars come from the platform

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="Shorten URLs with analytics, expiry, custom aliases and QR codes.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sinly.netlify.app",
        "http://localhost:5500",  
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router)
app.include_router(url_router) 


@app.get("/", tags=["health"])
def home():
    return {"status": "ok", "message": "URL Shortener API is running"}